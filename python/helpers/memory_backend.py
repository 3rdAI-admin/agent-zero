"""Abstract base class for memory storage backends.

Defines the interface that all memory backends (FAISS, SQLite, etc.) must implement.
The Memory class in memory.py orchestrates backends through this interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Sequence

from langchain_core.documents import Document


class MemoryBackend(ABC):
    """Abstract memory storage backend.

    All backends must support:
    - Semantic similarity search with score threshold
    - Document CRUD (insert, update, delete by ID, delete by query)
    - Persistence (save/load)
    - Bulk document access (get_all_docs)

    Backends receive pre-configured embedding models and manage their own
    index structures internally.
    """

    @abstractmethod
    async def search_similarity_threshold(
        self,
        query: str,
        limit: int,
        threshold: float,
        filter_fn: Any | None = None,
    ) -> list[Document]:
        """Search for documents by semantic similarity above a threshold.

        Args:
            query: The search query text.
            limit: Maximum number of results.
            threshold: Minimum similarity score (0.0 to 1.0).
            filter_fn: Optional callable(metadata_dict) -> bool for filtering.

        Returns:
            list[Document]: Matching documents with metadata.
        """

    @abstractmethod
    async def insert_documents(self, docs: list[Document], ids: list[str]) -> list[str]:
        """Insert documents with pre-assigned IDs.

        Args:
            docs: Documents to insert (metadata already populated).
            ids: Corresponding document IDs.

        Returns:
            list[str]: The inserted IDs.
        """

    @abstractmethod
    async def delete_by_ids(self, ids: list[str]) -> list[Document]:
        """Delete documents by their metadata IDs.

        Args:
            ids: Document IDs to delete.

        Returns:
            list[Document]: The deleted documents (for logging/undo).
        """

    @abstractmethod
    async def update_documents(self, docs: list[Document], ids: list[str]) -> None:
        """Update existing documents (delete + re-insert with same IDs).

        Args:
            docs: Updated documents.
            ids: Corresponding document IDs.
        """

    @abstractmethod
    def get_by_ids(self, ids: Sequence[str]) -> list[Document]:
        """Retrieve documents by IDs (synchronous).

        Args:
            ids: One or more document IDs.

        Returns:
            list[Document]: Found documents (missing IDs silently skipped).
        """

    @abstractmethod
    def get_all_docs(self) -> dict[str, Document]:
        """Return all documents in the store.

        Returns:
            dict[str, Document]: Mapping of docstore ID -> Document.
        """

    @abstractmethod
    def save(self) -> None:
        """Persist the current state to disk."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed a single query text.

        Args:
            text: Text to embed.

        Returns:
            list[float]: Embedding vector.
        """

    async def aget_by_ids(self, ids: Sequence[str]) -> list[Document]:
        """Async wrapper for get_by_ids (default implementation).

        Args:
            ids: Document IDs to retrieve.

        Returns:
            list[Document]: Found documents.
        """
        return self.get_by_ids(ids)

    @abstractmethod
    def add_documents_sync(self, docs: list[Document], ids: list[str]) -> None:
        """Synchronous document insertion (used during initialization/reindexing).

        Args:
            docs: Documents to insert.
            ids: Corresponding document IDs.
        """
