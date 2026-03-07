# 🤖 Multi-Agent Framework

A pluggable, growable LLM-based multi-agent system with:
- **Agent Registry** — drop in new agents with one file
- **Sequential → Hierarchical** routing
- **Persistent Memory** per agent
- **RAG** (retrieval-augmented generation) document store
- **Tool Registry** per agent
- **Evaluation & Observability** with Agent Stability Index (ASI)
- **FastAPI backend** + **React frontend** (GitHub Pages ready)

---

## 🗂 Repo Structure

```
mas-framework/
├── agents/
│   ├── base_agent.py          # BaseAgent class — extend this
│   ├── registry.py            # Agent registry — add agents here
│   └── builtin/               # Built-in specialist agents
│       ├── orchestrator_agent.py
│       ├── researcher_agent.py
│       ├── planner_agent.py
│       ├── executor_agent.py
│       └── critic_agent.py
├── memory/
│   └── memory_store.py        # Per-agent persistent memory (JSON → swap for Redis)
├── rag/
│   └── rag_store.py           # Document store with keyword retrieval
├── tools/
│   └── tool_registry.py       # Pluggable tools per agent
├── orchestrator/
│   └── pipeline.py            # Sequential/hierarchical pipeline runner
├── eval/
│   └── agent_metrics.py       # ASI drift metrics & observability
├── api/
│   └── main.py                # FastAPI backend (all routes)
├── frontend/
│   └── index.html             # React UI — works standalone or on GitHub Pages
├── tests/
├── notebooks/
├── .github/workflows/ci.yml   # CI + GitHub Pages auto-deploy
└── requirements.txt
```

---

## 🚀 Quick Start

### 1. Clone & install
```bash
git clone https://github.com/YOUR_USERNAME/mas-framework
cd mas-framework
pip install -r requirements.txt
cp .env.example .env  # add your API key
```

### 2. Run the backend
```bash
uvicorn api.main:app --reload --port 8000
```

### 3. Open the frontend
```bash
open frontend/index.html
# or visit http://localhost:8000/ui
```

### 4. Demo mode (no API key)
Just open `frontend/index.html` directly — the UI runs fully simulated in-browser.

---

## ➕ Adding a New Agent

1. Create `agents/builtin/my_agent.py`:
```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    agent_id = "my_agent"
    name = "My Agent"
    role = "Does something specific"
    icon = "◆"
    color = "#f97316"

    @property
    def system_prompt(self) -> str:
        return "You are MyAgent. Your role is..."
```

2. Register in `agents/registry.py`:
```python
from agents.builtin.my_agent import MyAgent
REGISTRY["my_agent"] = MyAgent
```

3. Optionally add to `DEFAULT_PIPELINE`.

That's it — the API and UI pick it up automatically.

---

## 🔌 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/agents` | List all registered agents |
| POST | `/run` | Run the pipeline |
| GET | `/run/{run_id}` | Get run result |
| GET | `/metrics` | Cross-agent ASI metrics |
| POST | `/rag/add` | Add a RAG document |
| GET | `/rag/list` | List RAG documents |
| GET | `/memory/{agent_id}` | Inspect agent memory |

### Run the pipeline via API:
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task": "Build a REST API", "api_key": "sk-ant-...", "simulate": false}'
```

---

## 📊 Agent Stability Index (ASI)

Each agent run is scored across 4 dimensions:

| Dimension | Description | Weight |
|-----------|-------------|--------|
| Response Consistency | Output length variance over recent runs | 30% |
| Reasoning Stability | Keyword overlap with prior outputs | 25% |
| Task Adherence | Task keyword coverage in output | 35% |
| Latency Stability | Elapsed time variance | 10% |

**ASI = weighted mean (0–100).** View in the Metrics tab of the UI.

---

## 🌐 GitHub Pages Deployment

The frontend auto-deploys via GitHub Actions on every push to `main`.

1. Go to **Settings → Pages → Source → GitHub Actions**
2. Add your `ANTHROPIC_API_KEY` to **Settings → Secrets**
3. Push to `main` — the UI is live at `https://YOUR_USERNAME.github.io/mas-framework/`

The frontend works in **demo mode** without a backend — no server required for GitHub Pages.

---

## 🛣 Roadmap

- [ ] Hierarchical orchestration (dynamic agent selection)
- [ ] Streaming API responses (SSE)
- [ ] Embedding-based RAG (sentence-transformers / ChromaDB)
- [ ] A2A (Agent-to-Agent) direct messaging
- [ ] Persistent run storage (SQLite / PostgreSQL)
- [ ] Evaluation pipeline with multi-run drift reports
- [ ] Docker Compose for one-command deployment

---

## 📄 License
MIT
