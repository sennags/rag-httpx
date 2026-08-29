"""Interface web local para consultar o Mini-RAG."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, request

from main import RAGApplication


PROJECT_DIR = Path(__file__).parent
load_dotenv(PROJECT_DIR / ".env")
app = Flask(__name__)
rag = RAGApplication(PROJECT_DIR / "data" / "httpx")
prepared = False


def prepare_rag() -> None:
    global prepared
    if not prepared:
        rag.prepare_index()
        prepared = True


@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    results = []
    answer = None
    error = None
    low_evidence = False

    if request.method == "POST":
        question = request.form.get("question", "")
        top_k = int(request.form.get("top_k", "3"))
        generate = request.form.get("generate") == "on"
        try:
            prepare_rag()
            results = rag.retrieval_agent.search(question, top_k)
            low_evidence = not rag.retrieval_agent.has_sufficient_evidence(results)
            if generate and not low_evidence:
                answer = rag.generate_answer(question, results)
        except (RuntimeError, ValueError) as exception:
            error = str(exception)

    return render_template(
        "index.html",
        question=question,
        results=results,
        answer=answer,
        error=error,
        low_evidence=low_evidence,
    )


if __name__ == "__main__":
    app.run(debug=True)
