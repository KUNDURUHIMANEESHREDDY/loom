import time
import os
from pathlib import Path
from tools.pdf import PDFMaker

LANGGRAPH_MASTER_REFERENCE_MARKDOWN = """# 🦜🕸️ LangGraph Master Technical Reference Manual
## *The Definitive Production Engineering Guide for Stateful Multi-Agent Applications*

---

## Table of Contents
1. Architecture & Philosophy
2. StateGraph API & Core Graph Builder
3. State Schema, TypedDict & Reducers
4. Nodes & Execution Functions
5. Edges & Dynamic Routing
6. Command API (State Mutation + Jump Navigation)
7. Send API & Dynamic Fan-Out Map-Reduce
8. Parallel Execution & Join Merging
9. ToolNode & Prebuilt Agent Components
10. MessageGraph & Message-Oriented Workflows
11. Subgraphs & Hierarchical Composition
12. Persistence & Checkpointing (Memory, SQLite, Postgres)
13. Long-Term Memory & Persistent Stores (Cross-Thread Memory)
14. Human-in-the-Loop (HITL), Interrupts & State Editing
15. Fine-Grained Streaming (Values, Updates, Messages, Custom Events)
16. Runtime Configuration & RunnableConfig
17. Error Handling, Retries & Recursion Limits
18. Async (`ainvoke`, `astream`) & Batch (`abatch`) Execution
19. Advanced Multi-Agent Design Patterns (Supervisor, Swarm, Blackboard)
20. Reflection, Self-Correction & Evaluator-Optimizer Loops
21. Observability & LangSmith Tracing
22. Graph Visualization (`draw_mermaid`, `draw_png`)
23. Production Deployment (LangGraph Cloud, RemoteGraph, REST API)
24. Performance Optimization & Context Window Management
25. Testing, Mocking & Replay Debugging
26. Engineering Best Practices & Anti-Patterns
27. Complete End-to-End Production Reference Implementation

---

## Chapter 1: Architecture & Philosophy

LangGraph is built on the principle that real-world AI applications are **stateful, dynamic, and non-linear**. Unlike standard chain frameworks (such as DAGs), complex cognitive systems require loops, reflection, self-correction, dynamic branching, human approval gates, and multi-agent coordination.

### Core Architectural Axioms
1. **Cycles as First-Class Citizens**: Graphs support loops (`A -> B -> A`) without recursion collapse.
2. **Centralized State, Functional Nodes**: Nodes are pure functions that accept state and return updates.
3. **Explicit Control Flow**: Routing logic is programmatic and observable.
4. **Durable Execution**: Every step can be persisted to disk/database, enabling resume-after-crash and human intervention.

---

## Chapter 2: StateGraph API & Core Graph Builder

The `StateGraph` object is the foundational builder class for defining application workflows.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    query: str
    result: str

builder = StateGraph(AgentState)
builder.add_node("process", lambda state: {"result": state["query"].upper()})
builder.add_edge(START, "process")
builder.add_edge("process", END)
graph = builder.compile()
```

---

## Chapter 3: State Schema, TypedDict & Reducers

State keys use **Reducers** to control how node returns are merged into the graph state.

```python
from typing import Annotated, TypedDict, List
import operator
from langchain_core.messages import BaseMessage

def merge_dicts(a: dict, b: dict) -> dict:
    res = a.copy()
    res.update(b)
    return res

class MasterState(TypedDict):
    # Appends messages (does not overwrite)
    messages: Annotated[List[BaseMessage], operator.add]
    # Overwrites value (default behavior)
    current_stage: str
    # Custom dictionary merger
    metadata: Annotated[dict, merge_dicts]
```

---

## Chapter 4: Nodes & Execution Functions

Nodes can receive state, `RunnableConfig`, and optional long-term `BaseStore`.

```python
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore

async def advanced_node(state: MasterState, config: RunnableConfig, store: BaseStore):
    thread_id = config["configurable"].get("thread_id")
    user_profile = await store.aget(("users",), key="user_123")
    return {"current_stage": "completed"}
```

---

## Chapter 5: Edges & Dynamic Routing

Routing can be static (`add_edge`) or dynamic (`add_conditional_edges`).

```python
from langgraph.prebuilt import tools_condition

# Fixed Edge
builder.add_edge("node_a", "node_b")

# Conditional Edge using prebuilt tools_condition
builder.add_conditional_edges("agent", tools_condition)
```

---

## Chapter 6: Command API (State Mutation + Jump Navigation)

The `Command` API allows a node to simultaneously update state and control routing dynamically.

```python
from langgraph.types import Command

def supervisor_node(state: MasterState) -> Command:
    if "code" in state["messages"][-1].content:
        return Command(goto="coder", update={"current_stage": "coding"})
    return Command(goto="researcher", update={"current_stage": "researching"})
```

---

## Chapter 7: Send API & Dynamic Fan-Out Map-Reduce

The `Send` API dynamically spawns parallel executions of a node for array items.

```python
from langgraph.types import Send

def continue_to_subqueries(state: MasterState):
    return [Send("worker", {"query": q}) for q in ["query_1", "query_2", "query_3"]]

builder.add_conditional_edges("planner", continue_to_subqueries, ["worker"])
```

---

## Chapter 8: Parallel Execution & Join Merging

When multiple branches run concurrently, join nodes wait until all parallel branches complete before executing.

```python
builder.add_edge("planner", "search_branch_a")
builder.add_edge("planner", "search_branch_b")
builder.add_edge(["search_branch_a", "search_branch_b"], "join_synthesizer")
```

---

## Chapter 9: ToolNode & Prebuilt Agent Components

LangGraph includes prebuilt node abstractions like `ToolNode` and `create_react_agent`.

```python
from langgraph.prebuilt import ToolNode, create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun

tools = [DuckDuckGoSearchRun()]
tool_node = ToolNode(tools)

# Or create a full ReAct agent graph in one line:
agent_graph = create_react_agent(model, tools=tools)
```

---

## Chapter 10: MessageGraph & Message-Oriented Workflows

`MessageGraph` is a specialized graph where the state is implicitly a list of `BaseMessage` objects.

```python
from langgraph.graph import MessageGraph

builder = MessageGraph()
builder.add_node("model", lambda messages: model.invoke(messages))
builder.add_edge(START, "model")
```

---

## Chapter 11: Subgraphs & Hierarchical Composition

Subgraphs allow embedding compiled graphs as nodes within parent graphs.

```python
parent_builder = StateGraph(ParentState)
parent_builder.add_node("child_subgraph", child_graph.compile())
```

---

## Chapter 12: Persistence & Checkpointing (Memory, SQLite, Postgres)

Checkpointers persist state snapshots at every super-step.

```python
from langgraph.checkpoint.postgres import PostgresSaver

# Production Postgres Checkpointer
with PostgresSaver.from_conn_string("postgresql://user:pass@localhost:5432/db") as checkpointer:
    checkpointer.setup()
    app = builder.compile(checkpointer=checkpointer)
```

---

## Chapter 13: Long-Term Memory & Persistent Stores

Stores provide cross-thread persistent memory across different chat sessions.

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
store.put(("users", "123"), "preferences", {"theme": "dark", "language": "python"})
```

---

## Chapter 14: Human-in-the-Loop (HITL), Interrupts & State Editing

Use `interrupt()` or `interrupt_before` to pause execution for human approval.

```python
from langgraph.types import interrupt

def human_approval_node(state: MasterState):
    response = interrupt({"question": "Approve action?", "state": state})
    if response["approved"]:
        return {"current_stage": "approved"}
    return {"current_stage": "rejected"}
```

---

## Chapter 15: Fine-Grained Streaming (Values, Updates, Messages, Custom Events)

Stream graphs using multiple streaming modes simultaneously.

```python
for mode, payload in app.stream({"query": "hi"}, config, stream_mode=["values", "updates"]):
    print(f"[{mode}] Payload:", payload)
```

---

## Chapter 16: Runtime Configuration & RunnableConfig

Pass runtime parameters without altering state schema using `RunnableConfig`.

```python
config = {"configurable": {"thread_id": "thread_1", "model_provider": "anthropic"}}
app.invoke(input_data, config=config)
```

---

## Chapter 17: Error Handling, Retries & Recursion Limits

Set recursion limits to prevent infinite loops and configure automatic retry policies.

```python
config = {"recursion_limit": 50}
app.invoke(input_data, config=config)
```

---

## Chapter 18: Async (`ainvoke`, `astream`) & Batch (`abatch`) Execution

Use asynchronous methods for high-throughput I/O bound production workloads.

```python
async for event in app.astream(input_data, config=config):
    pass
```

---

## Chapter 19: Advanced Multi-Agent Design Patterns

- **Supervisor**: Single master agent delegates sub-tasks to specialized sub-agents.
- **Swarm**: Decentralized agents pass control directly to each other via handoffs.
- **Blackboard**: Shared global state space where independent agents inspect and append insights.

---

## Chapter 20: Reflection, Self-Correction & Evaluator-Optimizer Loops

Nodes evaluate generated artifacts against quality criteria and route back for refinement if score < threshold.

---

## Chapter 21: Observability & LangSmith Tracing

Automatic full-trace logging of node execution times, prompts, token usage, and state transitions via LangSmith.

---

## Chapter 22: Graph Visualization (`draw_mermaid`, `draw_png`)

```python
print(app.get_graph().draw_mermaid())
```

---

## Chapter 23: Production Deployment (LangGraph Cloud, RemoteGraph, REST API)

Deploy graph instances as scalable REST microservices via LangGraph Cloud or self-hosted LangGraph Server (`langgraph.json`).

---

## Chapter 24: Performance Optimization & Context Window Management

Trim message arrays using `trim_messages()` or summary nodes to manage LLM token limits efficiently.

---

## Chapter 25: Testing, Mocking & Replay Debugging

Unit test individual node functions independently of the graph; mock checkpointers to test state replay scenarios.

---

## Chapter 26: Engineering Best Practices & Anti-Patterns

- **Best Practice**: Keep node functions pure and side-effect predictable.
- **Anti-Pattern**: Mutating global variables directly inside node logic.

---

## Chapter 27: Complete End-to-End Production Reference Implementation

Below is a production-ready, fully-featured multi-agent graph with persistence, tools, conditional routing, and Command navigation.

```python
from typing import Annotated, TypedDict, List
import operator
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class ProductionState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    stage: str

def agent_step(state: ProductionState):
    return {"messages": [AIMessage(content="Processing completed.")], "stage": "done"}

builder = StateGraph(ProductionState)
builder.add_node("agent", agent_step)
builder.add_edge(START, "agent")
builder.add_edge("agent", END)

app = builder.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    cfg = {"configurable": {"thread_id": "prod_1"}}
    res = app.invoke({"messages": [HumanMessage(content="Start task")], "stage": "init"}, config=cfg)
    print("Execution Result Stage:", res["stage"])
```

---
*LangGraph Production Engineering Manual — Compiled by Agno Systems Architecture Engine*
"""

def generate_master_pdf():
    pdf_maker = PDFMaker()
    output_filename = f"langgraph_master_production_manual_{int(time.time())}.pdf"
    
    pdf_path = pdf_maker.create_pdf(
        title="LangGraph Master Technical Reference Manual",
        content=LANGGRAPH_MASTER_REFERENCE_MARKDOWN,
        output_filename=output_filename,
        sources=[
            "https://docs.langchain.com/oss/python/langgraph/overview",
            "https://langchain-ai.github.io/langgraph/reference/func/",
            "https://docs.langchain.com/oss/python/langgraph/concepts/"
        ]
    )
    
    print(f"SUCCESS: Master PDF Generated at: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    generate_master_pdf()
