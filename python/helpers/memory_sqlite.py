"""SQLite-based memory backend with FTS5 full-text search and vec0 vector similarity.

Uses sqlite-vec for cosine similarity search and FTS5 for keyword search.
All data persists in a single memory.db file per memory subdirectory.
"""

import json
import os
import sqlite3
import struct
from typing import Any, Sequence

from langchain_core.documents import Document

import models
from python.helpers.memory_backend import MemoryBackend
from python.helpers.print_style import PrintStyle

try:
    import sqlite_vec
    from sqlite_vec import serialize_float32

    HAS_SQLITE_VEC = True
except ImportError:
    HAS_SQLITE_VEC = False

    def serialize_float32(vec: list[float]) -> bytes:
        """Fallback serializer if sqlite_vec not installed."""
        return struct.pack(f"{len(vec)}f", *vec)


def _deserialize_float32(blob: bytes) -> list[float]:
    """Deserialize a float32 blob to a list of floats."""
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


class SQLiteMemoryBackend(MemoryBackend):
    """SQLite-based memory backend with FTS5 + vec0 vector search.

    Schema:
    - documents: Main table (id TEXT PK, content TEXT, metadata TEXT)
    - documents_fts: FTS5 virtual table synced via triggers
    - documents_vec: vec0 virtual table for cosine similarity
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        db_path: str,
        embedder: Any,
        dimensions: int,
    ):
        self._conn = conn
        self._db_path = db_path
        self._embedder = embedder
        self._dimensions = dimensions

    @staticmethod
    def initialize(
        model_config: "models.ModelConfig",
        db_dir: str,
        in_memory: bool = False,
    ) -> tuple["SQLiteMemoryBackend", bool]:
        """Initialize a SQLite backend.

        Args:
            model_config: Embedding model configuration.
            db_dir: Absolute path to the database directory.
            in_memory: If True, use in-memory database.

        Returns:
            Tuple of (SQLiteMemoryBackend, created: bool).
        """
        if not HAS_SQLITE_VEC:
            raise ImportError(
                "sqlite-vec is required for SQLite memory backend. "
                "Install with: pip install sqlite-vec"
            )

        os.makedirs(db_dir, exist_ok=True)

        db_path = ":memory:" if in_memory else os.path.join(db_dir, "memory.db")
        created = not os.path.exists(db_path) if not in_memory else True

        conn = sqlite3.connect(db_path)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)

        # Enable WAL mode for better concurrent read performance
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")

        embeddings_model = models.get_embedding_model(
            model_config.provider,
            model_config.name,
            **model_config.build_kwargs(),
        )

        # Determine embedding dimensions
        dimensions = len(embeddings_model.embed_query("example"))
        PrintStyle.standard(
            f"SQLite memory backend: {dimensions}d embeddings, db={db_path}"
        )

        # Check for embedding model mismatch
        _handle_embedding_mismatch(conn, model_config, embeddings_model, dimensions)

        # Create tables
        _create_tables(conn, dimensions)

        backend = SQLiteMemoryBackend(
            conn=conn,
            db_path=db_path,
            embedder=embeddings_model,
            dimensions=dimensions,
        )
        return backend, created

    # ── MemoryBackend interface ──────────────────────────────────────────

    async def search_similarity_threshold(
        self,
        query: str,
        limit: int,
        threshold: float,
        filter_fn: Any | None = None,
    ) -> list[Document]:
        """Search by cosine similarity above threshold.

        Args:
            query: Search query text.
            limit: Maximum results.
            threshold: Minimum cosine similarity (0.0 to 1.0).
            filter_fn: Optional callable(metadata_dict) -> bool.

        Returns:
            list[Document]: Matching documents sorted by similarity.
        """
        query_embedding = self._embedder.embed_query(query)
        # Reason: sqlite-vec cosine distance is 0-2, threshold is similarity 0-1.
        # Convert: max_distance = 1.0 - threshold (e.g., 0.7 sim → 0.3 max dist)
        max_distance = 1.0 - threshold

        # Fetch more than needed if filtering, to account for filtered-out results
        fetch_k = limit * 3 if filter_fn else limit

        rows = self._conn.execute(
            """
            SELECT d.id, d.content, d.metadata, v.distance
            FROM documents_vec v
            LEFT JOIN documents d ON d.rowid = v.doc_rowid
            WHERE v.embedding MATCH ?
              AND k = ?
            ORDER BY v.distance
            """,
            [serialize_float32(query_embedding), fetch_k],
        ).fetchall()

        results: list[Document] = []
        for row in rows:
            if row[3] > max_distance:
                continue
            if row[0] is None:
                continue

            metadata = json.loads(row[2]) if row[2] else {}

            if filter_fn and not filter_fn(metadata):
                continue

            doc = Document(page_content=row[1], metadata=metadata)
            results.append(doc)

            if len(results) >= limit:
                break

        return results

    async def insert_documents(self, docs: list[Document], ids: list[str]) -> list[str]:
        """Insert documents with embeddings into SQLite."""
        for doc, doc_id in zip(docs, ids):
            content = doc.page_content
            metadata = json.dumps(doc.metadata)
            embedding = self._embedder.embed_query(content)

            self._conn.execute(
                "INSERT OR REPLACE INTO documents (id, content, metadata) VALUES (?, ?, ?)",
                [doc_id, content, metadata],
            )
            rowid = self._conn.execute(
                "SELECT rowid FROM documents WHERE id = ?", [doc_id]
            ).fetchone()[0]

            self._conn.execute(
                "INSERT OR REPLACE INTO documents_vec (doc_rowid, embedding) VALUES (?, ?)",
                [rowid, serialize_float32(embedding)],
            )

        self._conn.commit()
        return ids

    async def delete_by_ids(self, ids: list[str]) -> list[Document]:
        """Delete documents by ID."""
        deleted: list[Document] = []

        for doc_id in ids:
            row = self._conn.execute(
                "SELECT rowid, content, metadata FROM documents WHERE id = ?",
                [doc_id],
            ).fetchone()

            if row:
                rowid, content, meta_json = row
                metadata = json.loads(meta_json) if meta_json else {}
                deleted.append(Document(page_content=content, metadata=metadata))

                self._conn.execute(
                    "DELETE FROM documents_vec WHERE doc_rowid = ?", [rowid]
                )
                self._conn.execute("DELETE FROM documents WHERE id = ?", [doc_id])

        if deleted:
            self._conn.commit()
        return deleted

    async def update_documents(self, docs: list[Document], ids: list[str]) -> None:
        """Update documents by deleting and re-inserting."""
        await self.delete_by_ids(ids)
        await self.insert_documents(docs, ids)

    def get_by_ids(self, ids: Sequence[str]) -> list[Document]:
        """Retrieve documents by ID."""
        results: list[Document] = []
        for doc_id in ids:
            row = self._conn.execute(
                "SELECT content, metadata FROM documents WHERE id = ?", [doc_id]
            ).fetchone()
            if row:
                metadata = json.loads(row[1]) if row[1] else {}
                results.append(Document(page_content=row[0], metadata=metadata))
        return results

    def get_all_docs(self) -> dict[str, Document]:
        """Return all documents as {id: Document}."""
        rows = self._conn.execute(
            "SELECT id, content, metadata FROM documents"
        ).fetchall()

        result: dict[str, Document] = {}
        for row in rows:
            metadata = json.loads(row[2]) if row[2] else {}
            result[row[0]] = Document(page_content=row[1], metadata=metadata)
        return result

    def save(self) -> None:
        """Commit any pending changes."""
        self._conn.commit()

    def embed_query(self, text: str) -> list[float]:
        """Embed query text."""
        return self._embedder.embed_query(text)

    def add_documents_sync(self, docs: list[Document], ids: list[str]) -> None:
        """Synchronous document insertion for initialization/migration."""
        for doc, doc_id in zip(docs, ids):
            content = doc.page_content
            metadata = json.dumps(doc.metadata)
            embedding = self._embedder.embed_query(content)

            self._conn.execute(
                "INSERT OR REPLACE INTO documents (id, content, metadata) VALUES (?, ?, ?)",
                [doc_id, content, metadata],
            )
            rowid = self._conn.execute(
                "SELECT rowid FROM documents WHERE id = ?", [doc_id]
            ).fetchone()[0]

            self._conn.execute(
                "INSERT OR REPLACE INTO documents_vec (doc_rowid, embedding) VALUES (?, ?)",
                [rowid, serialize_float32(embedding)],
            )

        self._conn.commit()

    # ── FTS5 search (bonus, not in base interface) ───────────────────────

    async def search_fulltext(
        self,
        query: str,
        limit: int = 10,
        filter_fn: Any | None = None,
    ) -> list[Document]:
        """Full-text search using FTS5.

        Args:
            query: FTS5 search query.
            limit: Maximum results.
            filter_fn: Optional metadata filter.

        Returns:
            list[Document]: Matching documents.
        """
        rows = self._conn.execute(
            """
            SELECT d.id, d.content, d.metadata, fts.rank
            FROM documents_fts fts
            JOIN documents d ON d.rowid = fts.rowid
            WHERE documents_fts MATCH ?
            ORDER BY fts.rank
            LIMIT ?
            """,
            [query, limit],
        ).fetchall()

        results: list[Document] = []
        for row in rows:
            metadata = json.loads(row[2]) if row[2] else {}
            if filter_fn and not filter_fn(metadata):
                continue
            results.append(Document(page_content=row[1], metadata=metadata))

        return results

    def get_document_count(self) -> int:
        """Get total document count."""
        row = self._conn.execute("SELECT COUNT(*) FROM documents").fetchone()
        return row[0] if row else 0

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()


# ── Schema and migration helpers ─────────────────────────────────────────


def _create_tables(conn: sqlite3.Connection, dimensions: int) -> None:
    """Create the documents, FTS5, and vec0 tables if they don't exist.

    Args:
        conn: SQLite connection with sqlite-vec loaded.
        dimensions: Embedding vector dimensions.
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            metadata TEXT DEFAULT '{}'
        )
    """)

    # FTS5 for full-text search, synced with documents via triggers
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
            content,
            content='documents',
            content_rowid='rowid'
        )
    """)

    # Triggers to keep FTS5 in sync with documents table
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS documents_fts_ai
        AFTER INSERT ON documents BEGIN
            INSERT INTO documents_fts(rowid, content)
            VALUES (new.rowid, new.content);
        END
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS documents_fts_ad
        AFTER DELETE ON documents BEGIN
            INSERT INTO documents_fts(documents_fts, rowid, content)
            VALUES ('delete', old.rowid, old.content);
        END
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS documents_fts_au
        AFTER UPDATE ON documents BEGIN
            INSERT INTO documents_fts(documents_fts, rowid, content)
            VALUES ('delete', old.rowid, old.content);
            INSERT INTO documents_fts(rowid, content)
            VALUES (new.rowid, new.content);
        END
    """)

    # vec0 for vector similarity search
    try:
        conn.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_vec USING vec0(
                doc_rowid INTEGER PRIMARY KEY,
                embedding float[{dimensions}] distance_metric=cosine
            )
        """)
    except sqlite3.OperationalError:
        # Reason: Older sqlite-vec versions may not support IF NOT EXISTS
        # for virtual tables. Table already exists, safe to continue.
        pass

    # Embedding model metadata table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS embedding_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()


def _handle_embedding_mismatch(
    conn: sqlite3.Connection,
    model_config: "models.ModelConfig",
    embeddings_model: Any,
    dimensions: int,
) -> None:
    """Check for embedding model changes and handle reindexing.

    Args:
        conn: SQLite connection.
        model_config: Current embedding model config.
        embeddings_model: The embedding model instance.
        dimensions: Expected embedding dimensions.
    """
    try:
        row = conn.execute(
            "SELECT value FROM embedding_meta WHERE key = 'model_info'"
        ).fetchone()
    except sqlite3.OperationalError:
        # Table doesn't exist yet (first init)
        return

    if row:
        stored = json.loads(row[0])
        if (
            stored.get("model_provider") == model_config.provider
            and stored.get("model_name") == model_config.name
        ):
            return  # Model matches, no action needed

        PrintStyle.standard(
            f"Embedding model changed: {stored.get('model_name')} -> {model_config.name}. "
            "Reindexing..."
        )

        # Save all documents for reindexing
        docs_rows = conn.execute(
            "SELECT id, content, metadata FROM documents"
        ).fetchall()

        if docs_rows:
            # Drop and recreate vec0 table with new dimensions
            conn.execute("DROP TABLE IF EXISTS documents_vec")
            conn.execute(f"""
                CREATE VIRTUAL TABLE documents_vec USING vec0(
                    doc_rowid INTEGER PRIMARY KEY,
                    embedding float[{dimensions}] distance_metric=cosine
                )
            """)

            # Reindex all documents
            for doc_row in docs_rows:
                doc_id, content, _ = doc_row
                embedding = embeddings_model.embed_query(content)
                rowid = conn.execute(
                    "SELECT rowid FROM documents WHERE id = ?", [doc_id]
                ).fetchone()[0]
                conn.execute(
                    "INSERT INTO documents_vec (doc_rowid, embedding) VALUES (?, ?)",
                    [rowid, serialize_float32(embedding)],
                )

            PrintStyle.standard(f"Reindexed {len(docs_rows)} documents.")

    # Update stored model info
    conn.execute(
        "INSERT OR REPLACE INTO embedding_meta (key, value) VALUES (?, ?)",
        [
            "model_info",
            json.dumps(
                {
                    "model_provider": model_config.provider,
                    "model_name": model_config.name,
                }
            ),
        ],
    )
    conn.commit()
