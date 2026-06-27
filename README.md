# CodeForge AI

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40-FF4B4B.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-1C3C3C.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**A multi-agent AI platform that automates the software development lifecycle** — from requirement analysis to deployment — using 7 specialized agents orchestrated through LangGraph, with Hybrid RAG for context-aware code generation.

---

## 📸 Screenshots

> _Add your screenshots/demo GIF here before submitting._

| Dashboard | Agent Pipeline | Document Upload |
|---|---|---|
| `screenshot-dashboard.png` | `screenshot-pipeline.png` | `screenshot-upload.png` |

---

## ✨ Features

- **7-Agent Pipeline** — Requirement Analyzer → Planner → Code Generator → Bug Fixer → Documentation → Testing → Deployment, all orchestrated via LangGraph
- **Hybrid RAG** — combines FAISS (semantic search) and BM25 (keyword search) for more accurate context retrieval
- **Document Ingestion** — upload PDF, TXT, MD, or PY files; the system chunks, embeds, and indexes them for retrieval-augmented generation, with an AI-generated summary and preview shown immediately after upload
- **Guardrails** — input validation and sanitization, plus output validation before returning generated code
- **Conversation Memory** — per-session history persisted to disk, automatically included as context in follow-up requests
- **Live Agent Pipeline Visualization** — animated, real-time status of all 7 agents as they process a request
- **LLM Observability** — every agent call is traced via Langfuse (prompt, response, latency, token usage), viewable in the Langfuse dashboard
- **RAG Quality Evaluation** — standalone RAGAS script (`ragas_eval.py`) measures Faithfulness and Context Precision of the hybrid retriever against real uploaded documents
- **Dark, SaaS-style Dashboard** — 3-column layout (workflow sidebar, output console, system status) built with Streamlit and custom CSS

---

## 🛠️ Tech Stack

**AI / Orchestration**
- Llama 3.3 (via Groq API)
- LangGraph — multi-agent orchestration
- LangChain

**Retrieval**
- FAISS — vector similarity search
- BM25 (rank-bm25) — keyword search
- Hybrid retriever combining both

**Backend**
- FastAPI
- Pydantic — data validation and structured agent state
- Uvicorn — ASGI server
- httpx — async HTTP client (frontend → backend)

**Frontend**
- Streamlit
- Custom CSS (dark theme, animated pipeline, hover effects)

**Documents**
- pypdf — PDF text extraction
- langchain-text-splitters — chunking

**Other**
- python-dotenv, loguru, pytest
- Langfuse — LLM observability and tracing
- RAGAS — RAG quality evaluation (Faithfulness, Context Precision)

---

## 📁 Project Structure

```
codeforge-ai/
├── Agents/              # Individual agent implementations (BaseAgent + 7 specialized agents)
├── Backend/             # FastAPI app (main.py) — /chat, /upload, /health, /history endpoints
├── Frontend/            # Streamlit dashboard (app.py)
├── Graph/               # LangGraph workflow definition (AgentState, graph wiring)
├── Guardrails/          # Input/output validation
├── Memory/              # Per-session conversation history (JSON-file based)
├── RAG/                 # Ingestion, vector store (FAISS), hybrid retriever (FAISS + BM25)
├── Tools/                # Shared utility functions
├── Models/              # Pydantic schemas / data models
├── Prompts/             # Agent system prompts
├── Tests/               # pytest test suite
├── data/                # Runtime data (uploads, memory, vector index) — gitignored
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- A [Groq API key](https://console.groq.com) (free tier available)

### 1. Clone and set up the environment

```bash
git clone <your-repo-url>
cd codeforge-ai
python -m venv venv
```

**Activate the virtual environment:**

Windows (PowerShell):
```powershell
.\venv\Scripts\activate
```
If you get an execution policy error, run this once first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

macOS/Linux:
```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

### 4. Run the backend

```bash
python -m uvicorn Backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/health` to confirm it's running.

### 5. Run the frontend

In a **separate terminal** (with the venv activated again):

```bash
cd Frontend
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

> **Note:** Both the backend and frontend must be running simultaneously, each in its own terminal, for the app to work.

---

## 🐳 Running with Docker

```bash
docker-compose up --build
```

---

## 🧪 Running Tests

```bash
pytest Tests/
```

---

## 📖 How It Works

1. **You describe what to build** — either by typing a prompt or selecting one of the Quick Examples (Todo API, Auth System, Data Pipeline, URL Shortener)
2. **Guardrails validate the input** for safety before it reaches any agent
3. **RAG retrieval** pulls relevant context from any documents you've uploaded, combined with conversation memory from the current session
4. **The 7-agent pipeline runs sequentially:**
   - **Requirement Analyzer** — extracts and clarifies what's being asked
   - **Planner** — designs the implementation approach and architecture
   - **Code Generator** — writes the actual implementation
   - **Bug Fixer** — reviews and corrects the generated code
   - **Documentation** — produces docs/guides for the generated project
   - **Testing** — generates test cases
   - **Deployment** — produces deployment configuration (e.g. Docker Compose)
5. **Output validation** runs the generated code through Guardrails before it's returned
6. **Results appear** in the dashboard as expandable sections — Requirements, Plan, Code, Docs, Tests, Deploy, and raw JSON — each downloadable individually

---

## 📊 RAG Evaluation (RAGAS)

A standalone evaluation script (`ragas_eval.py`) measures the quality of the
Hybrid RAG pipeline using [RAGAS](https://github.com/vibrantlabsai/ragas):

- **Faithfulness** — is the generated answer grounded in retrieved context?
- **Context Precision** — are the retrieved chunks actually relevant to the query?

Run it with:
```bash
python ragas_eval.py
```

Sample results from a 3-question evaluation against an uploaded document:

| Metric | Average Score |
|---|---|
| Faithfulness | 0.821 |
| Context Precision | 0.667 |

Detailed per-question results are saved to `ragas_results.csv`. Each
question's answer-generation call is also traced in Langfuse (under the
`ragas-eval-question` trace name), with the Faithfulness and Context
Precision scores attached directly to that trace — visible in Langfuse's
**Scores** tab alongside the live app's agent traces.

> **Note:** the installed `ragas` package has a known upstream bug where
> `ragas/llms/base.py` imports `ChatVertexAI` from a `langchain_community`
> module path that no longer exists in current releases
> ([tracked upstream](https://github.com/vibrantlabsai/ragas/issues/2741)).
> Since this project doesn't use Vertex AI, the fix was a minimal local
> patch: removing the unused `ChatVertexAI`/`VertexAI` imports and their
> entry in `MULTIPLE_COMPLETION_SUPPORTED`. Separately, RAGAS's
> `ResponseRelevancy` metric was excluded because it requests multiple
> completions (`n>1`) in a single call, which Groq's API does not support.

## 🔮 Future Improvements

- Cloud deployment (AWS/GCP) beyond local Docker
- Streaming responses for faster perceived latency
- Expand RAGAS evaluation with a larger, curated question set and ground-truth answers for more rigorous scoring

---

## 📄 License

MIT License — see `LICENSE` file for details.

---

## 👤 Author

Built by Lavanya Pirisingula.