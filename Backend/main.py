from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from Graph.workflow import graph, AgentState
from RAG.ingestion import ingest_file
from RAG.vector_store import vector_store
from RAG.hybrid_retriever import hybrid_retriever
from Guardrails.input_validator import validate_input, sanitize_input
from Guardrails.output_validator import validate_output
from Memory.manager import memory_manager
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from loguru import logger
import os
import shutil

load_dotenv()

app = FastAPI(title="CodeForge AI", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lightweight LLM instance reused for quick document summaries.
# Kept separate from the 7-agent pipeline since a summary doesn't need
# the full LangGraph workflow — just one fast call.
_summary_llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    temperature=0.2,
    max_tokens=200,
)


def generate_document_summary(text: str) -> str:
    """Generate a short 2-3 sentence summary of uploaded document text."""
    try:
        # Cap input so we don't send an entire huge PDF to the LLM —
        # the first ~6000 chars is plenty of context for a summary.
        excerpt = text[:6000]
        prompt = (
            "Summarize the following document in 2-3 concise sentences. "
            "Focus on what the document is about and its key points.\n\n"
            f"Document:\n{excerpt}"
        )
        response = _summary_llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        logger.error(f"Summary generation error: {e}")
        return "Summary unavailable (could not generate)."


@app.get("/")
def root():
    return {"message": "CodeForge AI v4.0 - Complete Multi-Agent Platform"}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "4.0.0",
        "agents": 7,
        "rag_chunks": len(vector_store.chunks),
        "features": [
            "Multi-Agent LangGraph",
            "Hybrid RAG",
            "Guardrails",
            "Memory Management",
            "PDF Ingestion",
        ]
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        os.makedirs("data/uploads", exist_ok=True)
        file_path = f"data/uploads/{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        chunks = ingest_file(file_path)
        vector_store.add_documents(chunks)

        # Build a preview from the first couple of chunks (plain strings)
        full_preview_text = " ".join(chunks[:3])
        preview = full_preview_text[:500]
        if len(full_preview_text) > 500:
            preview += "..."

        # Generate a short AI summary from a larger excerpt of the chunks
        summary_source_text = " ".join(chunks[:15])
        summary = generate_document_summary(summary_source_text)

        return {
            "status": "ok",
            "filename": file.filename,
            "chunks_added": len(chunks),
            "total_chunks": len(vector_store.chunks),
            "preview": preview,
            "summary": summary,
        }
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/documents")
def list_documents():
    return {"total_chunks": len(vector_store.chunks), "status": "ok"}

@app.delete("/documents")
def clear_documents():
    vector_store.clear()
    return {"status": "ok", "message": "All documents cleared"}

@app.get("/history/{session_id}")
def get_history(session_id: str):
    history = memory_manager.get_history(session_id)
    return {"session_id": session_id, "history": history}

@app.delete("/history/{session_id}")
def clear_history(session_id: str):
    memory_manager.clear(session_id)
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: dict):
    message = request.get("message", "")
    session_id = request.get("session_id", "default")

    # Guardrails - Input validation
    is_valid, validation_msg = validate_input(message)
    if not is_valid:
        logger.warning(f"Input blocked: {validation_msg}")
        return {
            "session_id": session_id,
            "response": f"⚠️ {validation_msg}",
            "status": "blocked",
            "artifacts": {}
        }

    # Sanitize input
    message = sanitize_input(message)

    # Get conversation memory
    memory_context = memory_manager.get_context_string(session_id)

    # Get RAG context
    rag_context = hybrid_retriever.retrieve(message, k=3)

    # Build enriched message
    enriched_message = message
    if memory_context:
        enriched_message = f"{memory_context}\nCurrent Request: {message}"
    if rag_context:
        enriched_message += f"\n\nRelevant Knowledge Base Context:\n{rag_context}"

    initial_state: AgentState = {
        "user_query": enriched_message,
        "session_id": session_id,
        "current_agent": "start",
        "requirements": None,
        "plan": None,
        "generated_code": None,
        "fixed_code": None,
        "documentation": None,
        "test_cases": None,
        "deployment_config": None,
        "final_response": None,
        "error": None,
    }

    try:
        final_state = graph.invoke(initial_state)

        # Validate output with guardrails
        code = final_state.get("fixed_code") or final_state.get("generated_code", "")
        safe_code = validate_output(code)

        # Save to memory
        memory_manager.add_message(session_id, "user", message)
        memory_manager.add_message(session_id, "assistant", safe_code[:300])

        return {
            "session_id": session_id,
            "response": safe_code,
            "agent_used": final_state.get("current_agent", ""),
            "rag_used": bool(rag_context),
            "memory_used": bool(memory_context),
            "artifacts": {
                "requirements": final_state.get("requirements"),
                "plan": final_state.get("plan"),
                "code": safe_code,
                "documentation": validate_output(final_state.get("documentation", "") or ""),
                "tests": final_state.get("test_cases"),
                "deployment": final_state.get("deployment_config"),
            },
            "status": "ok"
        }
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        return {"error": str(e), "status": "error"}