"""Avaliacao simples e reproduzivel da recuperacao semantica."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from main import RAGApplication


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    expected_source: str


EVALUATION_CASES = (
    EvaluationCase(
        "Como desativar o timeout de uma requisicao?",
        "docs/advanced/timeouts.md",
    ),
    EvaluationCase(
        "Como configurar autenticacao basica em uma requisicao HTTPX?",
        "docs/advanced/authentication.md",
    ),
    EvaluationCase(
        "Como fazer uma requisicao assincrona com HTTPX?",
        "docs/async.md",
    ),
    EvaluationCase(
        "Como configurar um proxy HTTP no cliente?",
        "docs/advanced/proxies.md",
    ),
    EvaluationCase(
        "Como habilitar HTTP/2 no HTTPX?",
        "docs/http2.md",
    ),
    EvaluationCase(
        "Como configurar tentativas de conexao com um transporte customizado?",
        "docs/advanced/transports.md",
    ),
    EvaluationCase(
        "Quais sao as classes de excecao disponiveis no HTTPX?",
        "docs/exceptions.md",
    ),
    EvaluationCase(
        "Como enviar parametros na URL de uma requisicao?",
        "docs/quickstart.md",
    ),
)


def main() -> None:
    repository_dir = Path(__file__).with_name("data") / "httpx"
    application = RAGApplication(repository_dir)
    application.prepare_index()

    hits = 0
    for number, case in enumerate(EVALUATION_CASES, start=1):
        results = application.retrieval_agent.search(case.question, top_k=3)
        retrieved_sources = [result.chunk.source_path for result in results]
        hit = case.expected_source in retrieved_sources
        hits += hit

        status = "ACERTO" if hit else "ERRO"
        print(f"\nCaso {number}: {status}")
        print(f"Pergunta: {case.question}")
        print(f"Fonte esperada: {case.expected_source}")
        print("Fontes no top 3: " + ", ".join(retrieved_sources))

    total = len(EVALUATION_CASES)
    print(f"\nResultado final: {hits}/{total} fontes esperadas no top 3.")


if __name__ == "__main__":
    main()
