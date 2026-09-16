# Agno 🧵

**Agno** is an AI agent system powered by Knowledge Graphs, Hybrid RAG Retrieval, and Multi-Provider LLM Integration (**Google Gemini**, **DeepSeek**, **Groq**, and **Ollama**).

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```

Edit `.env`:
```env
LLM_PROVIDER=google  # google, deepseek, groq, ollama, or mock
GOOGLE_API_KEY=your_key_here
```

### 3. Run Agno CLI
```bash
python main.py
```

Or specify a provider dynamically on startup:
```bash
python main.py --provider deepseek
python main.py --provider groq
python main.py --provider ollama
python main.py --provider mock
```

---

## 🛠️ Architecture

* **`config.py`**: Configuration loading via `pydantic-settings`.
* **`models/`**: Strongly-typed schemas (`Document`, `Chunk`, `Entity`, `Relation`, `Message`, `AgentResponse`).
* **`llm/`**: Unified provider client supporting Google, DeepSeek, Groq, Ollama, and fallback mock engine.
* **`core/`**: Orchestration state machine (`AgnoEngine`) and task planner (`Planner`).
