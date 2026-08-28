"""Recupera e prepara documentos para as proximas etapas do Mini-RAG."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class DocumentChunk:
    """Trecho pesquisavel e rastreavel da documentacao."""

    chunk_id: str
    text: str
    source_path: str
    section: str


@dataclass(frozen=True)
class SearchResult:
    """Resultado ordenado da busca semantica."""

    rank: int
    score: float
    chunk: DocumentChunk


class RetrievalAgent:
    """Especialista no corpus e, futuramente, na busca semantica."""

    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    minimum_evidence_score = 0.25

    def __init__(self) -> None:
        self._model = None
        self._chunks: list[DocumentChunk] = []
        self._embeddings = None

    def find_markdown_documents(self, repository_dir: Path) -> list[Path]:
        """Retorna os Markdown de docs/ em ordem deterministica."""
        docs_dir = repository_dir / "docs"
        if not docs_dir.is_dir():
            raise FileNotFoundError(
                f"A pasta de documentacao nao foi encontrada: {docs_dir}"
            )

        return sorted(path for path in docs_dir.rglob("*.md") if path.is_file())

    def build_chunks(
        self,
        repository_dir: Path,
        chunk_size: int = 80,
        overlap: int = 15,
    ) -> list[DocumentChunk]:
        """Le os Markdown e cria chunks por secao, preservando a origem."""
        if chunk_size <= 0:
            raise ValueError("O tamanho do chunk deve ser maior que zero.")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("O overlap deve ser maior ou igual a zero e menor que o chunk.")

        chunks: list[DocumentChunk] = []
        for document in self.find_markdown_documents(repository_dir):
            source_path = document.relative_to(repository_dir).as_posix()
            content = document.read_text(encoding="utf-8")
            for section, body in self._split_sections(content, document.stem):
                for text in self._split_into_chunks(section, body, chunk_size, overlap):
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"{source_path}:{len(chunks) + 1}",
                            text=text,
                            source_path=source_path,
                            section=section,
                        )
                    )
        return chunks

    def create_index(self, chunks: list[DocumentChunk]) -> None:
        """Gera embeddings normalizados para os chunks em memoria."""
        if not chunks:
            raise ValueError("O corpus esta vazio e nao pode ser indexado.")

        model = self._get_model()
        embeddings = model.encode(
            [chunk.text for chunk in chunks],
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        self._chunks = chunks
        self._embeddings = embeddings

    def search(self, question: str, top_k: int = 3) -> list[SearchResult]:
        """Retorna os chunks mais similares a uma pergunta valida."""
        question = question.strip()
        if not question:
            raise ValueError("A pergunta nao pode estar vazia.")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or not 3 <= top_k <= 5:
            raise ValueError("top_k deve ser um inteiro entre 3 e 5.")
        if self._embeddings is None:
            raise RuntimeError("O indice ainda nao foi criado. Indexe o corpus antes de buscar.")

        question_embedding = self._get_model().encode(
            question, normalize_embeddings=True
        )
        scores = self._embeddings @ question_embedding
        best_indexes = scores.argsort()[::-1][:top_k]
        return [
            SearchResult(
                rank=rank,
                score=float(scores[index]),
                chunk=self._chunks[index],
            )
            for rank, index in enumerate(best_indexes, start=1)
        ]

    def has_sufficient_evidence(self, results: list[SearchResult]) -> bool:
        """Indica se o melhor resultado supera o limiar experimental de evidencia."""
        return bool(results) and results[0].score >= self.minimum_evidence_score

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as error:
                raise RuntimeError(
                    "sentence-transformers nao esta instalado. Execute "
                    "pip install -r requirements.txt."
                ) from error
            self._model = SentenceTransformer(self.model_name)
        return self._model

    @staticmethod
    def _split_sections(content: str, fallback_section: str) -> list[tuple[str, str]]:
        sections: list[tuple[str, str]] = []
        section = fallback_section
        lines: list[str] = []
        inside_code_fence = False

        for line in content.splitlines():
            if line.strip().startswith("```"):
                inside_code_fence = not inside_code_fence
                lines.append(line)
                continue

            heading = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
            if heading and not inside_code_fence:
                if "\n".join(lines).strip():
                    sections.append((section, "\n".join(lines).strip()))
                section = heading.group(1)
                lines = []
            else:
                lines.append(line)

        if "\n".join(lines).strip():
            sections.append((section, "\n".join(lines).strip()))
        return sections

    @staticmethod
    def _split_into_chunks(
        section: str, body: str, chunk_size: int, overlap: int
    ) -> list[str]:
        words = body.split()
        chunks: list[str] = []
        start = 0

        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_body = " ".join(words[start:end])
            chunks.append(f"## {section}\n\n{chunk_body}")
            if end == len(words):
                break
            start = end - overlap

        return chunks
