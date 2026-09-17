import time
import os
import urllib.request
import json
from pathlib import Path
from tools.pdf import PDFMaker

LANGGRAPH_DOCUMENTATION_MARKDOWN = """# 🦜🕸️ LangGraph Official Technical Reference Guide
*Comprehensive Architecture Manual, StateGraph API, Persistence, Human-in-the-Loop, and Multi-Agent Patterns*

---

## Chapter 1: Introduction to LangGraph & Core Architecture

LangGraph is a framework built by LangChain designed to construct **stateful, multi-actor LLM applications**. Unlike linear chain models or DAG-only execution engines, LangGraph supports **cyclic graph execution**, enabling robust loops, iterative reasoning, self-correction, agentic planning, and multi-agent coordination.

### Key Architectural Primitives

1. **`StateGraph`**: The primary class used to define a workflow graph. It is parameterized by a state schema (typically a `TypedDict` or `Pydantic` BaseModel).
2. **State (`TypedDict`)**: Central data structure passed between nodes. Every node receives the current state and returns state mutations.
3. **Nodes (`add_node`)**: Python functions or runnable tools that receive the graph state, execute actions (LLM calls, web searches, DB operations), and return state updates.
4. **Edges (`add_edge`)**: Define fixed control flow paths between nodes.
5. **Conditional Edges (`add_conditional_edges`)**: Dynamic routing logic evaluated after a node finishes, determining the next step based on state conditions.
6. **`START` & `END`**: Special sentinel nodes marking entry and exit points of graph execution.

---

## Chapter 2: State Schema & Reducer Annotations

Graph state represents the memory of your application across turns. State keys use **Reducer Annotations** to define how node returns update existing state values.

### State Reducers in Python

```python
from typing import Annotated, TypedDict, List
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # 'operator.add' appends new messages to the existing list instead of overwriting
    messages: Annotated[List[BaseMessage], operator.add]
    next_step: str
    iteration_count: int
    user_approved: bool
```

### Key Reducer Patterns
- **Overwrite (Default)**: If no annotation is specified (`next_step: str`), the return value of a node replaces the key's value completely.
- **Append (`operator.add`)**: Merges lists (e.g. appending chat history messages).
- **Custom Reducer**: Functions that merge dictionaries or combine complex data structures.

---

## Chapter 3: Nodes, Edges & Graph Building

Building a LangGraph workflow involves instantiating `StateGraph`, adding nodes, connecting edges, and compiling into a runnable `CompiledGraph`.

```python
from langgraph.graph import StateGraph, START, END

# 1. Initialize Graph with State Schema
builder = StateGraph(AgentState)

# 2. Add Processing Nodes
def agent_node(state: AgentState):
    # LLM call or decision logic
    return {"messages": [("assistant", "I am processing your request...")]}

def tool_execution_node(state: AgentState):
    # Execute external tool
    return {"messages": [("tool", "Tool output result")]}

builder.add_node("agent", agent_node)
builder.add_node("tools", tool_execution_node)

# 3. Define Fixed Edges
builder.add_edge(START, "agent")

# 4. Define Conditional Edges (Routing)
def should_continue(state: AgentState) -> str:
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    }
)

builder.add_edge("tools", "agent")

# 5. Compile Graph
graph = builder.compile()
```

---

## Chapter 4: Persistence & Checkpointing

Checkpointers save state snapshots after every node execution. This provides **durable execution**, enabling state recovery, multi-turn chat memory, time-travel debugging, and human-in-the-loop interventions.

### Checkpointer Implementation

```python
from langgraph.checkpoint.memory import MemorySaver

# Initialize in-memory checkpointer (or SqliteSaver / PostgresSaver for production)
memory = MemorySaver()

# Compile graph with checkpointer
app = builder.compile(checkpointer=memory)

# Execute query with thread configuration
config = {"configurable": {"thread_id": "session_123"}}
output = app.invoke({"messages": [("user", "Hello!")]}, config=config)
```

### Time Travel & State Inspection

```python
# Fetch state history for session thread
state_history = list(app.get_state_history(config))

# Replay or update past state
past_checkpoint = state_history[-2]
app.update_state(config, {"user_approved": True}, as_node="agent")
```

---

## Chapter 5: Human-in-the-Loop (HITL) & Interrupts

LangGraph natively supports **Human-in-the-Loop** workflows. You can pause graph execution before or after specific nodes to request user approval, edit LLM tool arguments, or inspect intermediate state.

```python
# Compile graph with human interrupts
app = builder.compile(
    checkpointer=memory,
    interrupt_before=["tools"]  # Pause execution before running tool_execution_node
)

# Initial execution pauses before 'tools'
thread_config = {"configurable": {"thread_id": "task_456"}}
app.invoke({"messages": [("user", "Delete database record 99")]}, thread_config)

# Inspect paused state
current_state = app.get_state(thread_config)
print("Paused at next step:", current_state.next)  # Outputs: ('tools',)

# Resume execution after user approves
app.invoke(None, thread_config)
```

---

## Chapter 6: Streaming Modes & Subgraphs

LangGraph provides fine-grained streaming capabilities for real-time user experiences:

### Streaming Modes
1. **`stream_mode="values"`**: Emits full state dictionary after every step.
2. **`stream_mode="updates"`**: Emits only the state delta (mutations) produced by each node.
3. **`stream_mode="tokens"`**: Streams individual LLM tokens as they generate.

```python
# Stream updates node by node
for event in app.stream({"messages": [("user", "Analyze Q3 numbers")]}, config, stream_mode="updates"):
    for node_name, state_update in event.items():
        print(f"Node '{node_name}' finished. Updates:", state_update)
```

---

## Chapter 7: Multi-Agent Architecture Patterns

LangGraph excels at coordinating multiple specialized agents in collaborative configurations.

### 1. Supervisor Architecture
A central Supervisor LLM router receives user requests, delegates sub-tasks to specialized worker agents (e.g. `ResearchAgent`, `CoderAgent`), and aggregates their outputs.

### 2. Hierarchical Teams
Nested subgraphs where each team (e.g., `EngineeringTeam`, `QualityAssuranceTeam`) acts as a single node in a top-level parent graph.

### 3. Peer-to-Peer Network
Agents pass messages directly to each other dynamically based on task requirements until consensus or task completion is reached.

---

## Chapter 8: Complete Production Code Example

Below is a complete, production-ready LangGraph agent script featuring tools, persistence, and state tracking.

```python
import operator
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Define State
class State(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# Define Node Functions
def chatbot(state: State):
    return {"messages": [AIMessage(content="Hello! How can I help you today?")]}

# Build Workflow Graph
workflow = StateGraph(State)
workflow.add_node("chatbot", chatbot)
workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

# Persistence
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "demo_thread"}}
    res = app.invoke({"messages": [HumanMessage(content="Hi")]}, config=config)
    print("Agent Response:", res["messages"][-1].content)
```

---
*Generated by Loom System Architecture Engine — LangGraph Technical Documentation Export*
"""

def generate_pdf():
    pdf_maker = PDFMaker()
    output_filename = f"langgraph_complete_documentation_guide_{int(time.time())}.pdf"
    
    pdf_path = pdf_maker.create_pdf(
        title="LangGraph Official Technical Reference Guide",
        content=LANGGRAPH_DOCUMENTATION_MARKDOWN,
        output_filename=output_filename,
        sources=["https://docs.langchain.com/oss/python/langgraph/overview", "https://langchain-ai.github.io/langgraph/"]
    )
    
    print(f"SUCCESS: PDF Generated at: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    generate_pdf()
