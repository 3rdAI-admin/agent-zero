"""FAISS-based memory backend implementation.

Wraps LangChain's FAISS vectorstore with the MemoryBackend interface.
This is the original/default backend extracted from memory.py.
"""

import json
import os
from typing import Any, Sequence, Union

import faiss
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import InMemoryByteStore, LocalFileStore
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document

import models
from python.helpers import faiss_monkey_patch  # noqa: F401
from python.helpers import files
from python.helpers.memory_backend import MemoryBackend
from python.helpers.print_style import PrintStyle


class MyFaiss(FAISS):
    """Custom FAISS wrapper with docstore access and async support."""

    def get_by_ids(self, ids: Sequence[str], /) -> list[Document]:
        """Retrieve documents by IDs from the internal docstore."""
        return [
            self.docstore._dict[id]  # type: ignore[attr-defined]
            for id in (ids if isinstance(ids, list) else [ids])
            if id in self.docstore._dict  # type: ignore[attr-defined]
        ]

    async def aget_by_ids(self, ids: Sequence[str], /) -> list[Document]:
        """Async wrapper for get_by_ids."""
        return self.get_by_ids(ids)

    def get_all_docs(self) -> dict[str, Document]:
        """Return entire docstore dictionary."""
        return self.docstore._dict  # type: ignore


class FAISSMemoryBackend(MemoryBackend):
    """FAISS-based memory backend.

    Uses LangChain's FAISS vectorstore with cosine similarity,
    cached embeddings, and local file persistence.
    """

    def __init__(self, db: MyFaiss, db_dir: str):
        self._db = db
        self._db_dir = db_dir

    @staticmethod
    def _cosine_normalizer(val: float) -> float:
        """Map cosine similarity from [-1,1] to [0,1]."""
        res = (1 + val) / 2
        return max(0, min(1, res))

    @staticmethod
    def initialize(
        model_config: "models.ModelConfig",
        db_dir: str,
        in_memory: bool = False,
    ) -> tuple["FAISSMemoryBackend", bool]:
        """Initialize a FAISS backend from disk or create a new one.

        Args:
            model_config: Embedding model configuration.
            db_dir: Absolute path to the database directory.
            in_memory: If True, use in-memory byte store for embedding cache.

        Returns:
            Tuple of (FAISSMemoryBackend, created: bool).
        """
        em_dir = files.get_abs_path("tmp/memory/embeddings")
        os.makedirs(db_dir, exist_ok=True)

        if in_memory:
            store: Union[InMemoryByteStore, LocalFileStore] = InMemoryByteStore()
        else:
            os.makedirs(em_dir, exist_ok=True)
            store = LocalFileStore(em_dir)

        embeddings_model = models.get_embedding_model(
            model_config.provider,
            model_config.name,
            **model_config.build_kwargs(),
        )
        embeddings_model_id = files.safe_file_name(
            model_config.provider + "_" + model_config.name
        )

        embedder = CacheBackedEmbeddings.from_bytes_store(
            embeddings_model, store, namespace=embeddings_model_id
        )

        db: MyFaiss | None = None
        docs: dict[str, Document] | None = None
        created = False

        # Load existing index if present
        if os.path.exists(db_dir) and files.exists(db_dir, "index.faiss"):
            db = MyFaiss.load_local(
                folder_path=db_dir,
                embeddings=embedder,
                allow_dangerous_deserialization=True,
                distance_strategy=DistanceStrategy.COSINE,
                relevance_score_fn=FAISSMemoryBackend._cosine_normalizer,
            )  # type: ignore

            # Check for embedding model mismatch
            emb_ok = False
            emb_set_file = files.get_abs_path(db_dir, "embedding.json")
            if files.exists(emb_set_file):
                embedding_set = json.loads(files.read_file(emb_set_file))
                if (
                    embedding_set["model_provider"] == model_config.provider
                    and embedding_set["model_name"] == model_config.name
                ):
                    emb_ok = True

            # Mismatch: save docs for reindexing, discard old index
            if db and not emb_ok:
                docs = db.get_all_docs()
                db = None

        # Create new DB if needed
        if not db:
            dim = len(embedder.embed_query("example"))
            index = faiss.IndexFlatIP(dim)

            db = MyFaiss(
                embedding_function=embedder,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
                distance_strategy=DistanceStrategy.COSINE,
                relevance_score_fn=FAISSMemoryBackend._cosine_normalizer,
            )

            # Reindex existing docs after model change
            if docs:
                PrintStyle.standard("Indexing memories...")
                db.add_documents(documents=list(docs.values()), ids=list(docs.keys()))

            # Persist
            db.save_local(folder_path=db_dir)
            meta_file_path = files.get_abs_path(db_dir, "embedding.json")
            files.write_file(
                meta_file_path,
                json.dumps(
                    {
                        "model_provider": model_config.provider,
                        "model_name": model_config.name,
                    }
                ),
            )
            created = True

        return FAISSMemoryBackend(db, db_dir), created

    # ── MemoryBackend interface ──────────────────────────────────────────

    async def search_similarity_threshold(
        self,
        query: str,
        limit: int,
        threshold: float,
        filter_fn: Any | None = None,
    ) -> list[Document]:
        """Semantic search via FAISS with cosine similarity threshold."""
        return await self._db.asearch(
            query,
            search_type="similarity_score_threshold",
            k=limit,
            score_threshold=threshold,
            filter=filter_fn,
        )

    async def insert_documents(self, docs: list[Document], ids: list[str]) -> list[str]:
        """Insert documents into FAISS index."""
        await self._db.aadd_documents(documents=docs, ids=ids)
        self.save()
        return ids

    async def delete_by_ids(self, ids: list[str]) -> list[Document]:
        """Delete documents by ID from FAISS index."""
        rem_docs = await self._db.aget_by_ids(ids)
        if rem_docs:
            rem_ids = [doc.metadata["id"] for doc in rem_docs]
            await self._db.adelete(ids=rem_ids)
            self.save()
        return rem_docs

    async def update_documents(self, docs: list[Document], ids: list[str]) -> None:
        """Update documents by deleting and re-inserting."""
        await self._db.adelete(ids=ids)
        await self._db.aadd_documents(documents=docs, ids=ids)
        self.save()

    def get_by_ids(self, ids: Sequence[str]) -> list[Document]:
        """Retrieve documents by ID from FAISS docstore."""
        return self._db.get_by_ids(ids)

    def get_all_docs(self) -> dict[str, Document]:
        """Return all documents in the FAISS docstore."""
        return self._db.get_all_docs()

    def save(self) -> None:
        """Persist FAISS index to disk."""
        self._db.save_local(folder_path=self._db_dir)

    def embed_query(self, text: str) -> list[float]:
        """Embed query text using the configured embedding model."""
        return self._db.embedding_function.embed_query(text)  # type: ignore

    def add_documents_sync(self, docs: list[Document], ids: list[str]) -> None:
        """Synchronous document insertion for initialization."""
        self._db.add_documents(documents=list(docs), ids=list(ids))
        self.save()
