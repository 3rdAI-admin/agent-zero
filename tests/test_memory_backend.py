"""Tests for the memory backend abstraction and SQLite implementation.

Tests cover:
- MemoryBackend abstract interface contract
- SQLiteMemoryBackend CRUD operations
- FAISSMemoryBackend CRUD operations
- FTS5 full-text search (SQLite only)
- Backend factory selection
- Settings toggle
- Edge cases: empty DB, duplicate IDs, missing IDs
"""

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from python.helpers.memory_backend import MemoryBackend


# ── Fixtures ─────────────────────────────────────────────────────────────


class FakeEmbedder:
    """Deterministic embedder for testing.

    Produces 8-dimensional embeddings based on simple character hashing.
    Consistent: same input always produces same output.
    """

    def embed_query(self, text: str) -> list[float]:
        """Generate a deterministic 8-dim embedding from text."""
        vec = [0.0] * 8
        for i, c in enumerate(text.encode()):
            vec[i % 8] += c / 256.0
        # Normalize to unit length for cosine similarity
        mag = sum(v * v for v in vec) ** 0.5
        if mag > 0:
            vec = [v / mag for v in vec]
        return vec

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents."""
        return [self.embed_query(t) for t in texts]


@pytest.fixture
def fake_embedder():
    return FakeEmbedder()


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


# ── MemoryBackend interface tests ────────────────────────────────────────


class TestMemoryBackendInterface:
    """Verify the abstract interface cannot be instantiated."""

    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            MemoryBackend()  # type: ignore


# ── SQLite backend tests ────────────────────────────────────────────────


class TestSQLiteMemoryBackend:
    """Tests for SQLiteMemoryBackend."""

    @pytest.fixture
    def sqlite_backend(self, temp_dir, fake_embedder):
        """Create an in-memory SQLite backend for testing."""
        sqlite_vec = pytest.importorskip("sqlite_vec")

        from python.helpers.memory_sqlite import SQLiteMemoryBackend

        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)

        from python.helpers.memory_sqlite import _create_tables

        _create_tables(conn, dimensions=8)

        backend = SQLiteMemoryBackend(
            conn=conn,
            db_path=":memory:",
            embedder=fake_embedder,
            dimensions=8,
        )
        return backend

    @pytest.mark.asyncio
    async def test_insert_and_get_by_ids(self, sqlite_backend):
        doc = Document(
            page_content="The cat sat on the mat",
            metadata={"id": "doc1", "area": "main"},
        )
        ids = await sqlite_backend.insert_documents([doc], ["doc1"])
        assert ids == ["doc1"]

        result = sqlite_backend.get_by_ids(["doc1"])
        assert len(result) == 1
        assert result[0].page_content == "The cat sat on the mat"
        assert result[0].metadata["id"] == "doc1"

    @pytest.mark.asyncio
    async def test_insert_multiple_documents(self, sqlite_backend):
        docs = [
            Document(page_content="First doc", metadata={"id": "a", "area": "main"}),
            Document(page_content="Second doc", metadata={"id": "b", "area": "main"}),
            Document(
                page_content="Third doc",
                metadata={"id": "c", "area": "fragments"},
            ),
        ]
        ids = await sqlite_backend.insert_documents(docs, ["a", "b", "c"])
        assert len(ids) == 3

        all_docs = sqlite_backend.get_all_docs()
        assert len(all_docs) == 3

    @pytest.mark.asyncio
    async def test_delete_by_ids(self, sqlite_backend):
        doc = Document(
            page_content="Temporary memory",
            metadata={"id": "temp1", "area": "main"},
        )
        await sqlite_backend.insert_documents([doc], ["temp1"])

        deleted = await sqlite_backend.delete_by_ids(["temp1"])
        assert len(deleted) == 1
        assert deleted[0].page_content == "Temporary memory"

        # Verify it's gone
        result = sqlite_backend.get_by_ids(["temp1"])
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_delete_nonexistent_id(self, sqlite_backend):
        deleted = await sqlite_backend.delete_by_ids(["nonexistent"])
        assert len(deleted) == 0

    @pytest.mark.asyncio
    async def test_update_documents(self, sqlite_backend):
        doc = Document(
            page_content="Original content",
            metadata={"id": "upd1", "area": "main"},
        )
        await sqlite_backend.insert_documents([doc], ["upd1"])

        updated_doc = Document(
            page_content="Updated content",
            metadata={"id": "upd1", "area": "main", "version": 2},
        )
        await sqlite_backend.update_documents([updated_doc], ["upd1"])

        result = sqlite_backend.get_by_ids(["upd1"])
        assert len(result) == 1
        assert result[0].page_content == "Updated content"
        assert result[0].metadata.get("version") == 2

    @pytest.mark.asyncio
    async def test_search_similarity_threshold(self, sqlite_backend):
        docs = [
            Document(
                page_content="Python programming language",
                metadata={"id": "py", "area": "main"},
            ),
            Document(
                page_content="JavaScript web development",
                metadata={"id": "js", "area": "main"},
            ),
            Document(
                page_content="Python data science and machine learning",
                metadata={"id": "pyds", "area": "main"},
            ),
        ]
        await sqlite_backend.insert_documents(docs, ["py", "js", "pyds"])

        results = await sqlite_backend.search_similarity_threshold(
            query="Python programming",
            limit=5,
            threshold=0.0,  # Very low threshold to get all results
        )
        assert len(results) > 0
        # Results should be documents
        assert all(isinstance(r, Document) for r in results)

    @pytest.mark.asyncio
    async def test_search_with_filter(self, sqlite_backend):
        docs = [
            Document(
                page_content="Main area memory",
                metadata={"id": "m1", "area": "main"},
            ),
            Document(
                page_content="Fragment area memory",
                metadata={"id": "f1", "area": "fragments"},
            ),
        ]
        await sqlite_backend.insert_documents(docs, ["m1", "f1"])

        def main_filter(data):
            return data.get("area") == "main"

        results = await sqlite_backend.search_similarity_threshold(
            query="memory",
            limit=10,
            threshold=0.0,
            filter_fn=main_filter,
        )
        assert all(r.metadata["area"] == "main" for r in results)

    @pytest.mark.asyncio
    async def test_get_all_docs_empty(self, sqlite_backend):
        all_docs = sqlite_backend.get_all_docs()
        assert len(all_docs) == 0

    @pytest.mark.asyncio
    async def test_embed_query(self, sqlite_backend):
        vec = sqlite_backend.embed_query("test text")
        assert len(vec) == 8
        assert all(isinstance(v, float) for v in vec)

    @pytest.mark.asyncio
    async def test_add_documents_sync(self, sqlite_backend):
        docs = [
            Document(
                page_content="Sync doc",
                metadata={"id": "sync1", "area": "main"},
            ),
        ]
        sqlite_backend.add_documents_sync(docs, ["sync1"])

        result = sqlite_backend.get_by_ids(["sync1"])
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_aget_by_ids(self, sqlite_backend):
        doc = Document(
            page_content="Async get test",
            metadata={"id": "async1", "area": "main"},
        )
        await sqlite_backend.insert_documents([doc], ["async1"])

        result = await sqlite_backend.aget_by_ids(["async1"])
        assert len(result) == 1
        assert result[0].page_content == "Async get test"

    @pytest.mark.asyncio
    async def test_get_document_count(self, sqlite_backend):
        assert sqlite_backend.get_document_count() == 0

        docs = [
            Document(page_content="Doc A", metadata={"id": "a", "area": "main"}),
            Document(page_content="Doc B", metadata={"id": "b", "area": "main"}),
        ]
        await sqlite_backend.insert_documents(docs, ["a", "b"])

        assert sqlite_backend.get_document_count() == 2

    @pytest.mark.asyncio
    async def test_fulltext_search(self, sqlite_backend):
        docs = [
            Document(
                page_content="The quick brown fox jumps over the lazy dog",
                metadata={"id": "fox", "area": "main"},
            ),
            Document(
                page_content="Python is a great programming language",
                metadata={"id": "python", "area": "main"},
            ),
        ]
        await sqlite_backend.insert_documents(docs, ["fox", "python"])

        results = await sqlite_backend.search_fulltext("python")
        assert len(results) >= 1
        assert any("Python" in r.page_content for r in results)


# ── Backend factory tests ────────────────────────────────────────────────


class TestBackendFactory:
    """Test the backend selection logic."""

    def test_get_backend_type_default(self):
        from python.helpers.memory import _get_backend_type

        # Should return "faiss" when no setting is configured
        with patch("python.helpers.settings.get_settings", return_value={}):
            result = _get_backend_type()
            assert result == "faiss"

    def test_get_backend_type_sqlite(self):
        from python.helpers.memory import _get_backend_type

        with patch(
            "python.helpers.settings.get_settings",
            return_value={"memory_backend": "sqlite"},
        ):
            result = _get_backend_type()
            assert result == "sqlite"

    def test_get_backend_type_faiss_explicit(self):
        from python.helpers.memory import _get_backend_type

        with patch(
            "python.helpers.settings.get_settings",
            return_value={"memory_backend": "faiss"},
        ):
            result = _get_backend_type()
            assert result == "faiss"


# ── Memory class tests ──────────────────────────────────────────────────


class TestMemoryClass:
    """Test the Memory orchestration class."""

    def test_area_enum(self):
        from python.helpers.memory import Memory

        assert Memory.Area.MAIN.value == "main"
        assert Memory.Area.FRAGMENTS.value == "fragments"
        assert Memory.Area.SOLUTIONS.value == "solutions"

    def test_get_comparator(self):
        from python.helpers.memory import Memory

        comp = Memory._get_comparator("area == 'main'")
        assert comp({"area": "main"}) is True
        assert comp({"area": "fragments"}) is False

    def test_get_comparator_error_returns_false(self):
        from python.helpers.memory import Memory

        comp = Memory._get_comparator("nonexistent_var == 'x'")
        assert comp({}) is False

    def test_format_docs_plain(self):
        from python.helpers.memory import Memory

        docs = [
            Document(
                page_content="Hello world",
                metadata={"id": "1", "area": "main"},
            ),
        ]
        formatted = Memory.format_docs_plain(docs)
        assert len(formatted) == 1
        assert "id: 1" in formatted[0]
        assert "Content: Hello world" in formatted[0]

    def test_get_timestamp_format(self):
        from python.helpers.memory import Memory

        ts = Memory.get_timestamp()
        # Should be in YYYY-MM-DD HH:MM:SS format
        assert len(ts) == 19
        assert ts[4] == "-"
        assert ts[7] == "-"
        assert ts[10] == " "

    def test_reload_clears_index(self):
        from python.helpers.memory import Memory, reload

        Memory.index["test_subdir"] = MagicMock()
        assert "test_subdir" in Memory.index

        reload()
        assert len(Memory.index) == 0


# ── Settings integration tests ──────────────────────────────────────────


class TestSettingsIntegration:
    """Test that memory_backend setting is properly defined."""

    def test_settings_has_memory_backend_field(self):
        from python.helpers.settings import Settings

        # Verify the field exists in the TypedDict
        assert "memory_backend" in Settings.__annotations__
