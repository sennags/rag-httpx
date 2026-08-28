"""Ponto de entrada do Mini-RAG sobre a documentacao do HTTPX."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from retrieval_agent import RetrievalAgent


HTTPX_REPOSITORY = "https://github.com/encode/httpx.git"
HTTPX_COMMIT = "b5addb64f0161ff6bfe94c124ef76f6a1fba5254"
EXPECTED_DOCUMENT_COUNT = 23


class RAGApplication:
    """Agente principal: prepara o corpus e coordena o RetrievalAgent."""

    def __init__(self, repository_dir: Path) -> None:
        self.repository_dir = repository_dir
        self.retrieval_agent = RetrievalAgent()

    def prepare_corpus(self) -> list[Path]:
        """Garante o commit exigido e delega a descoberta dos documentos."""
        self._obtain_httpx_repository()
        return self.retrieval_agent.find_markdown_documents(self.repository_dir)

    def _obtain_httpx_repository(self) -> None:
        if not self.repository_dir.exists():
            self.repository_dir.parent.mkdir(parents=True, exist_ok=True)
            self._run_git("clone", HTTPX_REPOSITORY, str(self.repository_dir))
        elif not (self.repository_dir / ".git").is_dir():
            raise RuntimeError(
                f"O caminho ja existe, mas nao e um repositorio Git: {self.repository_dir}"
            )

        self._run_git("-C", str(self.repository_dir), "fetch", "origin", HTTPX_COMMIT)
        self._run_git("-C", str(self.repository_dir), "checkout", "--detach", HTTPX_COMMIT)

    @staticmethod
    def _run_git(*arguments: str) -> None:
        try:
            subprocess.run(
                ["git", *arguments], check=True, text=True, capture_output=True
            )
        except subprocess.CalledProcessError as error:
            message = error.stderr.strip() or error.stdout.strip() or str(error)
            raise RuntimeError(f"Falha ao executar Git: {message}") from error


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepara a documentacao HTTPX para o Mini-RAG."
    )
    parser.add_argument(
        "--repository-dir",
        type=Path,
        default=Path("data/httpx"),
        help="Pasta local em que o repositorio HTTPX sera obtido.",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    application = RAGApplication(arguments.repository_dir)
    documents = application.prepare_corpus()

    print(f"Documentos Markdown encontrados: {len(documents)}")
    for document in documents:
        print(document.relative_to(application.repository_dir))

    if len(documents) == EXPECTED_DOCUMENT_COUNT:
        print("Validacao concluida: a contagem esperada e 23 arquivos.")
    else:
        print(
            "Atencao: eram esperados 23 arquivos. Verifique o commit e o caminho docs/."
        )


if __name__ == "__main__":
    main()
