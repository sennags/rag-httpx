"""Interface web local para consultar o Mini-RAG."""

from __future__ import annotations

import os
import subprocess
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
    top_k = "3"
    generator = ""
    results = []
    answer = None
    response_label = None
    error = None
    low_evidence = False

    if request.method == "POST":
        question = request.form.get("question", "")
        top_k = request.form.get("top_k", "3")
        generator = request.form.get("generator", "")
        try:
            prepare_rag()
        except (
            FileNotFoundError,
            OSError,
            RuntimeError,
            ValueError,
            subprocess.CalledProcessError,
        ) as exception:
            error = f"Nao foi possivel preparar o corpus: {exception}"
        else:
            try:
                results = rag.retrieval_agent.search(question, int(top_k))
                low_evidence = not rag.retrieval_agent.has_sufficient_evidence(results)
                if generator == "gemini" and not low_evidence:
                    answer = rag.generate_answer(question, results)
                    response_label = "RESPOSTA FUNDAMENTADA"
                if generator == "ollama" and not low_evidence:
                    answer = rag.generate_local_answer(question, results)
                    response_label = "RESPOSTA FUNDAMENTADA"
            except (
                FileNotFoundError,
                OSError,
                RuntimeError,
                ValueError,
                subprocess.CalledProcessError,
            ) as exception:
                error = f"Nao foi possivel executar a busca: {exception}"

    return render_template(
        "index.html",
        question=question,
        top_k=top_k,
        generator=generator,
        results=results,
        answer=answer,
        response_label=response_label,
        error=error,
        low_evidence=low_evidence,
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5050")),
        debug=False,
        threaded=False,
        use_reloader=False,
    )
