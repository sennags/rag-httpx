"""Recupera e prepara documentos para as proximas etapas do Mini-RAG."""

from __future__ import annotations

from pathlib import Path


class RetrievalAgent:
    """Especialista no corpus e, futuramente, na busca semantica."""

    def find_markdown_documents(self, repository_dir: Path) -> list[Path]:
        """Retorna os Markdown de docs/ em ordem deterministica."""
        docs_dir = repository_dir / "docs"
        if not docs_dir.is_dir():
            raise FileNotFoundError(
                f"A pasta de documentacao nao foi encontrada: {docs_dir}"
            )

        return sorted(path for path in docs_dir.rglob("*.md") if path.is_file())
