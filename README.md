# local-agent-kit

> A framework for building AI agents that run entirely on your local machine — no API keys, no cloud, no data leaving your device.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Powered by Ollama](https://img.shields.io/badge/powered%20by-Ollama-black.svg)](https://ollama.com)
[![LangGraph](https://img.shields.io/badge/built%20with-LangGraph-purple.svg)](https://langchain-ai.github.io/langgraph/)

---

## What is this?

`local-agent-kit` is a minimal, well-structured starting point for building LLM agents that:

- Run **100% locally** using [Ollama](https://ollama.com)
- Have **persistent memory** across sessions (3-layer architecture)
- Use **[LangGraph](https://langchain-ai.github.io/langgraph/)** for reliable, inspectable agent flow
- Are **fully configurable** via a single `.env` file
- Work on **low-end hardware** (tested on 4-core CPU, 8GB RAM)

This project is designed to be cloned, understood, and extended — not installed as a black-box library.

---

## Quick start

### 1. Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) running locally (or in Docker)

```bash
# Pull a model (llama3.2:3b recommended for low-end hardware)
ollama pull llama3.2:3b

# Or if you use Docker
docker exec ollama ollama pull llama3.2:3b
```

### 2. Clone and install

```bash
git clone https://github.com/pablobelmiro/agent-memory
cd local-agent-kit

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env if needed (default works out of the box with Ollama on localhost)
```

### 4. Run

```bash
python examples/simple_chat.py
```

```
Agent ready. Type 'exit' to quit.

You: my name is Lucas and I love Python
Agent: Nice to meet you, Lucas! Python is a great choice...

You: what's my name?
Agent: Your name is Lucas — you mentioned it earlier.
```

---

## Architecture

```
local-agent-kit/
│
├── agent/                  # Core framework
│   ├── graph.py            # LangGraph graph definition (start here)
│   ├── state.py            # Shared state (TypedDict)
│   ├── nodes.py            # Each graph node as an isolated function
│   ├── router.py           # Routing logic between nodes
│   └── prompts.py          # System prompt builder
│
├── memory/                 # 3-layer memory system
│   ├── manager.py          # Unified interface for all layers
│   ├── layer1_core.py      # Layer 1: always-in-context (core.json)
│   ├── layer2_topics.py    # Layer 2: on-demand topics (topics/*.json)
│   └── layer3_history.py   # Layer 3: raw history (*.jsonl, grep only)
│
├── tools/                  # Agent tools
│   ├── registry.py         # Central tool registry
│   ├── search_history.py   # Search past conversations
│   ├── calculator.py       # Simple math evaluation
│   └── datetime_tool.py    # Current date and time
│
├── config/
│   └── settings.py         # Reads .env and exposes typed constants
│
├── examples/
│   ├── simple_chat.py      # Basic chat loop (main entry point)
│   ├── custom_tools.py     # How to add your own tools
│   └── multi_model.py      # How to route between models
│
└── data/                   # Generated at runtime, git-ignored
    ├── memory/
    │   ├── core.json        # Layer 1
    │   └── topics/          # Layer 2
    └── history/             # Layer 3
```

### Agent flow

```
User input
    │
    ▼
load_memory ──► build_context ──► call_llm
                                      │
                           ┌──────────┤
                           │          │
                       [tool call] [final answer]
                           │          │
                        tools      save_memory
                           │          │
                           └──► call_llm    END
```

### Memory layers

| Layer | Storage | When loaded | Purpose |
|-------|---------|-------------|---------|
| 1 — Core | `core.json` | Every turn | Name, key facts, short notes |
| 2 — Topics | `topics/*.json` | On-demand | Domain knowledge, preferences per topic |
| 3 — History | `*.jsonl` | Grep only | Full raw transcripts, never loaded whole |

This design keeps the context window small and fast, even on low-end hardware.

---

## Configuration

All settings live in `.env`. Copy `.env.example` to get started.

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | `llama3.2:3b` | Model to use |
| `LLM_NUM_PREDICT` | `256` | Max tokens per response |
| `LLM_NUM_CTX` | `2048` | Context window size |
| `LLM_TEMPERATURE` | `0.7` | Sampling temperature |
| `LLM_NUM_THREAD` | `4` | CPU threads for inference |
| `AGENT_MAX_HISTORY_TURNS` | `3` | Conversation turns kept in context |
| `AGENT_MAX_ITERATIONS` | `10` | Max tool-call iterations per turn |
| `MEMORY_MAX_NOTES` | `20` | Max notes stored in layer 1 |

### Model recommendations by hardware

| RAM | Recommended model | `LLM_NUM_CTX` |
|-----|-------------------|---------------|
| 4 GB | `phi3:mini` (2.2GB) | `1024` |
| 8 GB | `llama3.2:3b` (2.0GB) | `2048` |
| 16 GB | `mistral:7b` (4.1GB) | `4096` |
| 32 GB+ | `llama3.1:8b` (4.7GB) | `8192` |

---

## Adding your own tools

Create a file in `tools/` and register it in `tools/registry.py`:

```python
# tools/my_tool.py
from langchain_core.tools import tool

@tool
def my_tool(input: str) -> str:
    """Describe what this tool does — the agent reads this description."""
    return f"Result: {input}"
```

```python
# tools/registry.py
from tools.my_tool import my_tool

_TOOLS = [
    search_history_tool,
    calculator_tool,
    datetime_tool,
    my_tool,          # ← add here
]
```

That's it. The agent will automatically know the tool is available.

---

## Extending the memory system

### Save a topic (Layer 2)

```python
from memory.manager import MemoryManager

mem = MemoryManager()
mem.topics.save("python", {
    "level": "intermediate",
    "interests": ["agents", "async", "type hints"]
})
```

### Search history (Layer 3)

```python
results = mem.search_history("LangGraph")
for r in results:
    print(r["ts"], r["role"], r["content"][:80])
```

---

## Hardware tested

| Machine | RAM | Tokens/s | Notes |
|---------|-----|----------|-------|
| AMD Ryzen 3 3250U | 8 GB | ~3.7 | CPU only, fully functional |
| Apple M1 | 8 GB | ~35 | MLX acceleration |
| Intel i7 + RTX 3060 | 16 GB | ~60 | GPU via CUDA |

---

## Roadmap

- [ ] Web UI (Gradio or Streamlit)
- [ ] RAG support (local vector store via ChromaDB)
- [ ] Multi-agent support (supervisor + specialized agents)
- [ ] autoDream: background memory consolidation
- [ ] REST API wrapper (FastAPI)

---

## Contributing

Pull requests are welcome. For major changes, open an issue first.

Please keep the project's philosophy in mind: **simple, local-first, hardware-aware.**

---

## License

[MIT](LICENSE) — use it, fork it, build on it.

---

## Acknowledgements

Built with [LangGraph](https://langchain-ai.github.io/langgraph/), [LangChain](https://www.langchain.com/), and [Ollama](https://ollama.com).
Inspired by the need to make AI agents accessible without cloud dependencies.
