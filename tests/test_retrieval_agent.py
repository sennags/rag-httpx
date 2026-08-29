import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from main import RAGApplication
from retrieval_agent import DocumentChunk, RetrievalAgent, SearchResult


class RetrievalAgentTests(unittest.TestCase):
    def test_build_chunks_preserves_metadata_and_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository_dir = Path(temporary_directory)
            docs_dir = repository_dir / "docs"
            docs_dir.mkdir()
            (docs_dir / "guide.md").write_text(
                "# Guide\n\none two three four five six seven",
                encoding="utf-8",
            )

            chunks = RetrievalAgent().build_chunks(
                repository_dir, chunk_size=5, overlap=2
            )

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].source_path, "docs/guide.md")
        self.assertEqual(chunks[0].section, "Guide")
        self.assertEqual(chunks[0].chunk_id, "docs/guide.md:1")
        self.assertIn("four five six seven", chunks[1].text)

    def test_code_comment_is_not_treated_as_markdown_heading(self) -> None:
        content = "# Guide\n\n```python\n# This is a comment\nvalue = 1\n```"

        sections = RetrievalAgent()._split_sections(content, "guide")

        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0][0], "Guide")
        self.assertIn("# This is a comment", sections[0][1])

    def test_search_rejects_empty_question_before_indexing(self) -> None:
        with self.assertRaisesRegex(ValueError, "pergunta nao pode estar vazia"):
            RetrievalAgent().search("   ")

    def test_search_rejects_a_very_short_question(self) -> None:
        with self.assertRaisesRegex(ValueError, "pelo menos 4 caracteres"):
            RetrievalAgent().search("oii")

    def test_search_rejects_invalid_top_k_before_indexing(self) -> None:
        with self.assertRaisesRegex(ValueError, "top_k deve ser um inteiro"):
            RetrievalAgent().search("Como usar HTTPX?", top_k=2)

    def test_search_requires_an_index(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "indice ainda nao foi criado"):
            RetrievalAgent().search("Como usar HTTPX?")

    def test_low_score_is_reported_as_insufficient_evidence(self) -> None:
        chunk = DocumentChunk("docs/guide.md:1", "text", "docs/guide.md", "Guide")
        result = SearchResult(rank=1, score=0.79, chunk=chunk)

        self.assertFalse(RetrievalAgent().has_sufficient_evidence([result]))

    def test_generation_requires_api_key(self) -> None:
        chunk = DocumentChunk("docs/guide.md:1", "text", "docs/guide.md", "Guide")
        result = SearchResult(rank=1, score=0.80, chunk=chunk)

        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY nao esta configurada"):
                RAGApplication(Path("unused")).generate_answer("Pergunta", [result])

    def test_cached_index_is_rejected_when_metadata_changes(self) -> None:
        chunk = DocumentChunk("docs/guide.md:1", "text", "docs/guide.md", "Guide")
        metadata = {"commit": "one", "model": "model", "chunk_size": 80}

        with tempfile.TemporaryDirectory() as temporary_directory:
            cache_path = Path(temporary_directory) / "rag_index.pkl"
            agent = RetrievalAgent()
            agent._chunks = [chunk]
            agent._embeddings = [[0.1]]
            agent.save_index(cache_path, metadata)

            self.assertTrue(RetrievalAgent().load_index(cache_path, metadata))
            self.assertFalse(
                RetrievalAgent().load_index(
                    cache_path, {"commit": "two", "model": "model", "chunk_size": 80}
                )
            )


if __name__ == "__main__":
    unittest.main()
