"""
RAGAS Evaluation Script for CodeForge AI's Hybrid RAG pipeline.

This is a standalone script, NOT part of the live FastAPI app. Run it
manually whenever you want to measure retrieval/generation quality —
it's not wired into every /chat request, since that would add latency
and cost to every single user interaction.

USAGE:
    1. Make sure you've already uploaded at least one document through
       the app (so vector_store.chunks is populated), OR run this from
       the project root where data/uploads already has ingested content
       from a previous session.
    2. Edit the `eval_questions` list below to match content that's
       actually relevant to whatever document(s) you've uploaded.
    3. Run:  python ragas_eval.py
    4. Scores print to console and save to ragas_results.csv

METRICS USED:
    - Faithfulness        : is the generated answer grounded in the
                             retrieved context, or hallucinated?
    - LLMContextPrecisionWithoutReference :
                             are the retrieved chunks actually relevant
                             to the query (vs. retrieval noise)?

NOTE: ResponseRelevancy was intentionally left out. It requires an
embedding model (e.g. sentence-transformers) and also internally
asks the judge LLM for multiple completions in one request (n>1),
which Groq's API rejects ("'n': number must be at most 1"). Adding
it back would need both a local embedding model and a workaround for
Groq's n=1 limit — skipped here to keep the dependency footprint
small and the evaluation reliable.

These two don't require pre-written "ground truth" answers, which
keeps this practical to run without building a labeled dataset first.
"""

import os
import sys
import asyncio

# Allow running this script from the project root.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from ragas.llms import LangchainLLMWrapper
from ragas import SingleTurnSample
from ragas.metrics import Faithfulness, LLMContextPrecisionWithoutReference

from RAG.hybrid_retriever import hybrid_retriever
from RAG.vector_store import vector_store

# get_client() gives access to Langfuse's scoring API (create_score),
# used below to push RAGAS's Faithfulness/Context Precision numbers
# into Langfuse's "Scores" feature, attached to the matching trace —
# separate from langfuse_handler, which only handles LangChain tracing.
from langfuse import get_client as get_langfuse_client

# Reuse the same Langfuse handler already configured in base_agent.py
# (it reads LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_HOST from
# .env and does its own auth check there). Importing it here means RAGAS
# eval calls show up in the same Langfuse project as the live app's
# agent traces, tagged separately so they're easy to tell apart.
from Agents.base_agent import langfuse_handler


# ── 1. Set up the judge LLM (the model that scores faithfulness/relevancy) ──
judge_llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    temperature=0,
    max_tokens=4096,  # RAGAS's internal prompts (e.g. breaking an answer
                      # into atomic statements, and its JSON "repair" step
                      # when the first parse fails) can need a lot of room
                      # — too low causes LLMDidNotFinishException mid-eval.
)

# NOTE: we deliberately do NOT use judge_llm.bind(config=...) here.
# .bind() wraps the model in a RunnableBinding, which would break
# RAGAS's internal isinstance()/hasattr() checks against the raw
# ChatGroq object (e.g. checking .temperature, or matching against
# MULTIPLE_COMPLETION_SUPPORTED). Since RAGAS's LangchainLLMWrapper
# manages its own call config internally and doesn't expose a way to
# inject extra callbacks into every internal call it makes, the
# judge LLM's own internal statement-generation / fix-output calls
# won't show up in Langfuse — only the directly-controlled
# generate_answer() calls below will. This is a reasonable tradeoff:
# you still get the RAG-answer-generation calls traced, which is the
# more interesting half of the RAGAS run anyway.
evaluator_llm = LangchainLLMWrapper(judge_llm)

faithfulness_metric = Faithfulness(llm=evaluator_llm)
context_precision_metric = LLMContextPrecisionWithoutReference(llm=evaluator_llm)


# ── 2. Define test questions ──────────────────────────────────────────────
# IMPORTANT: edit these to match whatever document(s) you've actually
# uploaded through the app. Generic/unrelated questions will score low
# on every metric simply because there's nothing relevant to retrieve —
# that's not a bug, it's the eval correctly reflecting irrelevant input.
eval_questions = [
    "What is this document about?",
    "What are the key skills mentioned?",
    "What programming languages are mentioned?",
]


# ── 3. Helper: run a question through retrieval + a quick LLM answer ───────
# We reuse RequirementAnalyzer's prompt style here just to get a real
# generated answer grounded in the retrieved context — this mirrors how
# your actual /chat endpoint enriches a query with RAG context before
# passing it to an agent.
def generate_answer(question: str, context: str) -> tuple[str, str | None]:
    """Returns (answer, trace_id). trace_id is None if Langfuse isn't
    configured, in which case scores simply won't be pushed later."""
    answer_llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        temperature=0.1,
        max_tokens=200,
    )
    prompt = (
        f"Answer the question using ONLY the context below, in 2-3 sentences. "
        f"Be concise. If the context doesn't contain the answer, say so.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    )

    invoke_config = {}
    if langfuse_handler is not None:
        invoke_config["callbacks"] = [langfuse_handler]
        invoke_config["metadata"] = {"langfuse_tags": ["ragas-answer-generation"]}

    if langfuse_handler is None:
        response = answer_llm.invoke(prompt, config=invoke_config)
        return response.content.strip(), None

    # Wrap the call in an explicit observation so we capture its
    # trace_id — needed to attach the Faithfulness/Context Precision
    # scores to this exact trace afterward, rather than them floating
    # unattached. (Note: this client version exposes
    # start_as_current_observation(), not start_as_current_span() —
    # the method name differs across recent Langfuse SDK releases.)
    langfuse_client = get_langfuse_client()
    with langfuse_client.start_as_current_observation(
        name="ragas-eval-question", as_type="span"
    ) as span:
        trace_id = span.trace_id
        response = answer_llm.invoke(prompt, config=invoke_config)
        span.update(input=question, output=response.content.strip())

    return response.content.strip(), trace_id


# ── 4. Run the evaluation ───────────────────────────────────────────────────
async def run_evaluation():
    if not vector_store.chunks:
        print(
            "\n⚠️  No documents found in the vector store.\n"
            "Upload a document through the app first (Frontend → Upload),\n"
            "or make sure data/uploads has been ingested in this session.\n"
        )
        return

    print(f"Vector store has {len(vector_store.chunks)} chunks loaded.\n")

    results = []
    for question in eval_questions:
        print(f"→ Question: {question}")

        # Retrieve context using the actual hybrid retriever
        context_string = hybrid_retriever.retrieve(question, k=4)
        if not context_string:
            print("  (no context retrieved, skipping)\n")
            continue

        # hybrid_retriever.retrieve() returns one joined string —
        # split it back into a list of individual chunks for RAGAS,
        # which expects retrieved_contexts as a list[str].
        contexts = [c.strip() for c in context_string.split("\n\n---\n\n") if c.strip()]

        # Generate an answer grounded in that context
        answer, trace_id = generate_answer(question, context_string)
        print(f"  Answer: {answer[:120]}{'...' if len(answer) > 120 else ''}")

        sample = SingleTurnSample(
            user_input=question,
            response=answer,
            retrieved_contexts=contexts,
        )

        # Wrapped so that if scoring fails for one question (e.g. a
        # transient LLMDidNotFinishException), we keep the results
        # already gathered for earlier questions instead of losing
        # the whole run.
        try:
            faithfulness_score = await faithfulness_metric.single_turn_ascore(sample)
            precision_score = await context_precision_metric.single_turn_ascore(sample)
        except Exception as e:
            print(f"  ⚠️  Scoring failed for this question, skipping: {e}\n")
            continue

        print(
            f"  Faithfulness: {faithfulness_score:.3f}  |  "
            f"Context Precision: {precision_score:.3f}\n"
        )

        # Push the RAGAS scores into Langfuse's "Scores" feature,
        # attached to this question's trace (captured in generate_answer
        # above). Without this, RAGAS's numbers only ever live in this
        # terminal output and the CSV — Langfuse's Scores tab stays
        # empty even though the traces themselves are present.
        if trace_id is not None and langfuse_handler is not None:
            try:
                langfuse_client = get_langfuse_client()
                langfuse_client.create_score(
                    trace_id=trace_id,
                    name="ragas_faithfulness",
                    value=float(faithfulness_score),
                    data_type="NUMERIC",
                    comment="RAGAS Faithfulness score",
                )
                langfuse_client.create_score(
                    trace_id=trace_id,
                    name="ragas_context_precision",
                    value=float(precision_score),
                    data_type="NUMERIC",
                    comment="RAGAS Context Precision score",
                )
            except Exception as e:
                print(f"  ⚠️  Could not push scores to Langfuse: {e}")

        results.append({
            "question": question,
            "answer": answer,
            "num_contexts": len(contexts),
            "faithfulness": faithfulness_score,
            "context_precision": precision_score,
        })

    if not results:
        print("No results to report — every question failed to retrieve context.")
        return

    # ── 5. Print summary ────────────────────────────────────────────────────
    avg_faith = sum(r["faithfulness"] for r in results) / len(results)
    avg_prec = sum(r["context_precision"] for r in results) / len(results)

    print("=" * 60)
    print("RAGAS EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Questions evaluated:        {len(results)}")
    print(f"Avg Faithfulness:           {avg_faith:.3f}")
    print(f"Avg Context Precision:      {avg_prec:.3f}")
    print("=" * 60)
    print(
        "\nReference: scores above ~0.8 are generally considered strong.\n"
        "Low Faithfulness  -> answers are hallucinating beyond the context.\n"
        "Low Precision     -> retrieved chunks contain too much irrelevant noise.\n"
    )

    # ── 6. Save to CSV for inclusion in your report/submission ────────────
    try:
        import csv
        with open("ragas_results.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)
        print("Saved detailed results to ragas_results.csv")
    except Exception as e:
        print(f"Could not save CSV: {e}")

    # ── 7. Flush Langfuse so traces actually get sent before exit ─────────
    # Langfuse batches/sends trace data in the background. A normal
    # FastAPI/Streamlit app stays running long enough for that background
    # flush to happen naturally, but this script runs once and exits
    # immediately — without an explicit flush, buffered trace data can be
    # lost when the process terminates before the background sender runs.
    if langfuse_handler is not None:
        try:
            get_langfuse_client().flush()
            print("Flushed pending Langfuse traces and scores.")
        except Exception as e:
            print(f"Langfuse flush failed (traces may not have been sent): {e}")


if __name__ == "__main__":
    asyncio.run(run_evaluation())