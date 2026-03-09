"""Memory orchestration layer.

The Memory class manages memory backends (FAISS, SQLite, etc.) through the
MemoryBackend abstract interface. It handles initialization, caching, knowledge
preloading, and document lifecycle — delegating storage to the active backend.
"""

from datetime import datetime
from typing import Any

import json
import logging
import os

from langchain_core.documents import Document

from python.helpers import files, guids, knowledge_import
from python.helpers.log import LogItem
from python.helpers.memory_backend import MemoryBackend
from python.helpers.print_style import PrintStyle
from enum import Enum
from agent import Agent, AgentContext
import models
from simpleeval import simple_eval

# Raise the log level so WARNING messages aren't shown
logging.getLogger("langchain_core.vectorstores.base").setLevel(logging.ERROR)


def _create_backend(
    model_config: "models.ModelConfig",
    memory_subdir: str,
    in_memory: bool = False,
    log_item: LogItem | None = None,
) -> tuple[MemoryBackend, bool]:
    """Create the appropriate memory backend based on settings.

    Args:
        model_config: Embedding model configuration.
        memory_subdir: Memory subdirectory name.
        in_memory: Whether to use in-memory storage.
        log_item: Optional log item for progress updates.

    Returns:
        Tuple of (MemoryBackend, created: bool).
    """
    # Reason: Import here to avoid circular imports and to support future
    # backend selection via settings (e.g., MEMORY_BACKEND=sqlite).

    backend_type = _get_backend_type()
    db_dir = abs_db_dir(memory_subdir)

    if backend_type == "sqlite":
        from python.helpers.memory_sqlite import SQLiteMemoryBackend

        return SQLiteMemoryBackend.initialize(
            model_config=model_config,
            db_dir=db_dir,
            in_memory=in_memory,
        )
    else:
        from python.helpers.memory_faiss import FAISSMemoryBackend

        return FAISSMemoryBackend.initialize(
            model_config=model_config,
            db_dir=db_dir,
            in_memory=in_memory,
        )


def _get_backend_type() -> str:
    """Read the memory backend type from settings.

    Returns:
        'faiss' (default) or 'sqlite'.
    """
    try:
        from python.helpers import settings

        s = settings.get_settings()
        return s.get("memory_backend", "faiss")  # type: ignore
    except Exception:
        return "faiss"


class Memory:
    class Area(Enum):
        MAIN = "main"
        FRAGMENTS = "fragments"
        SOLUTIONS = "solutions"

    # Cache: memory_subdir -> MemoryBackend
    index: dict[str, MemoryBackend] = {}

    @staticmethod
    async def get(agent: Agent) -> "Memory":
        """Get or initialize memory for an agent.

        Args:
            agent: The agent requesting memory access.

        Returns:
            Memory: Initialized memory wrapper.
        """
        memory_subdir = get_agent_memory_subdir(agent)
        if Memory.index.get(memory_subdir) is None:
            log_item = agent.context.log.log(
                type="util",
                heading=f"Initializing VectorDB in '/{memory_subdir}'",
            )
            PrintStyle.standard("Initializing VectorDB...")
            if log_item:
                log_item.stream(progress="\nInitializing VectorDB")

            backend, created = _create_backend(
                model_config=agent.config.embeddings_model,
                memory_subdir=memory_subdir,
                in_memory=False,
                log_item=log_item,
            )
            Memory.index[memory_subdir] = backend
            wrap = Memory(backend, memory_subdir=memory_subdir)
            knowledge_subdirs = get_knowledge_subdirs_by_memory_subdir(
                memory_subdir, agent.config.knowledge_subdirs or []
            )
            if knowledge_subdirs:
                await wrap.preload_knowledge(log_item, knowledge_subdirs, memory_subdir)
            return wrap
        else:
            return Memory(
                db=Memory.index[memory_subdir],
                memory_subdir=memory_subdir,
            )

    @staticmethod
    async def get_by_subdir(
        memory_subdir: str,
        log_item: LogItem | None = None,
        preload_knowledge: bool = True,
    ) -> "Memory":
        """Get or initialize memory by explicit subdirectory.

        Args:
            memory_subdir: Memory subdirectory name.
            log_item: Optional log item for progress updates.
            preload_knowledge: Whether to preload knowledge files.

        Returns:
            Memory: Initialized memory wrapper.
        """
        if not Memory.index.get(memory_subdir):
            import initialize

            agent_config = initialize.initialize_agent()
            model_config = agent_config.embeddings_model

            backend, _created = _create_backend(
                model_config=model_config,
                memory_subdir=memory_subdir,
                in_memory=False,
                log_item=log_item,
            )
            wrap = Memory(backend, memory_subdir=memory_subdir)
            if preload_knowledge:
                knowledge_subdirs = get_knowledge_subdirs_by_memory_subdir(
                    memory_subdir, agent_config.knowledge_subdirs or []
                )
                if knowledge_subdirs:
                    await wrap.preload_knowledge(
                        log_item, knowledge_subdirs, memory_subdir
                    )
            Memory.index[memory_subdir] = backend
        return Memory(db=Memory.index[memory_subdir], memory_subdir=memory_subdir)

    @staticmethod
    async def reload(agent: Agent) -> "Memory":
        """Clear cached backend and reinitialize from disk.

        Args:
            agent: The agent requesting reload.

        Returns:
            Memory: Freshly initialized memory wrapper.
        """
        memory_subdir = get_agent_memory_subdir(agent)
        if Memory.index.get(memory_subdir):
            del Memory.index[memory_subdir]
        return await Memory.get(agent)

    def __init__(
        self,
        db: MemoryBackend,
        memory_subdir: str,
    ):
        self.db = db
        self.memory_subdir = memory_subdir

    # ── Knowledge preloading ─────────────────────────────────────────────

    async def preload_knowledge(
        self, log_item: LogItem | None, kn_dirs: list[str], memory_subdir: str
    ) -> None:
        """Preload knowledge files into the memory backend.

        Args:
            log_item: Optional log item for progress updates.
            kn_dirs: Knowledge subdirectories to load.
            memory_subdir: Memory subdirectory name.
        """
        if log_item:
            log_item.update(heading="Preloading knowledge...")

        db_dir = abs_db_dir(memory_subdir)
        index_path = files.get_abs_path(db_dir, "knowledge_import.json")

        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        index: dict[str, knowledge_import.KnowledgeImport] = {}
        if os.path.exists(index_path):
            with open(index_path, "r") as f:
                index = json.load(f)

        index = self._preload_knowledge_folders(log_item, kn_dirs, index)

        for file in index:
            if index[file]["state"] in ["changed", "removed"] and index[file].get(
                "ids", []
            ):
                await self.delete_documents_by_ids(index[file]["ids"])
            if index[file]["state"] == "changed":
                index[file]["ids"] = await self.insert_documents(
                    index[file]["documents"]
                )

        # Remove entries for removed files
        index = {k: v for k, v in index.items() if v["state"] != "removed"}

        # Strip transient fields and persist index
        for file in index:
            if "documents" in index[file]:
                del index[file]["documents"]  # type: ignore
            if "state" in index[file]:
                del index[file]["state"]  # type: ignore
        with open(index_path, "w") as f:
            json.dump(index, f)

    def _preload_knowledge_folders(
        self,
        log_item: LogItem | None,
        kn_dirs: list[str],
        index: dict[str, knowledge_import.KnowledgeImport],
    ) -> dict[str, knowledge_import.KnowledgeImport]:
        """Load knowledge from directories, organized by area.

        Args:
            log_item: Optional log item for progress updates.
            kn_dirs: Knowledge subdirectories.
            index: Current knowledge import index.

        Returns:
            Updated knowledge import index.
        """
        for kn_dir in kn_dirs:
            # Root files go to MAIN area
            index = knowledge_import.load_knowledge(
                log_item,
                abs_knowledge_dir(kn_dir),
                index,
                {"area": Memory.Area.MAIN.value},
                filename_pattern="*",
                recursive=False,
            )
            # Subdirectories go to their named areas
            for area in Memory.Area:
                index = knowledge_import.load_knowledge(
                    log_item,
                    abs_knowledge_dir(kn_dir, area.value),
                    index,
                    {"area": area.value},
                    recursive=True,
                )
        return index

    # ── Document operations (delegate to backend) ────────────────────────

    def get_document_by_id(self, id: str) -> Document | None:
        """Retrieve a single document by ID.

        Args:
            id: Document ID.

        Returns:
            Document or None if not found.
        """
        docs = self.db.get_by_ids([id])
        return docs[0] if docs else None

    async def search_similarity_threshold(
        self, query: str, limit: int, threshold: float, filter: str = ""
    ) -> list[Document]:
        """Search for similar documents above a threshold.

        Args:
            query: Search query text.
            limit: Maximum results.
            threshold: Minimum similarity score.
            filter: Optional simpleeval filter expression.

        Returns:
            list[Document]: Matching documents.
        """
        comparator = Memory._get_comparator(filter) if filter else None
        return await self.db.search_similarity_threshold(
            query, limit, threshold, filter_fn=comparator
        )

    async def delete_documents_by_query(
        self, query: str, threshold: float, filter: str = ""
    ) -> list[Document]:
        """Delete documents matching a semantic query.

        Args:
            query: Search query text.
            threshold: Minimum similarity for deletion.
            filter: Optional simpleeval filter expression.

        Returns:
            list[Document]: Deleted documents.
        """
        k = 100
        tot = 0
        removed: list[Document] = []

        while True:
            docs = await self.search_similarity_threshold(
                query, limit=k, threshold=threshold, filter=filter
            )
            removed += docs

            document_ids = [result.metadata["id"] for result in docs]

            if document_ids:
                await self.db.delete_by_ids(document_ids)
                tot += len(document_ids)

            if len(document_ids) < k:
                break

        return removed

    async def delete_documents_by_ids(self, ids: list[str]) -> list[Document]:
        """Delete documents by their IDs.

        Args:
            ids: Document IDs to delete.

        Returns:
            list[Document]: Deleted documents.
        """
        return await self.db.delete_by_ids(ids)

    async def insert_text(self, text: str, metadata: dict = {}) -> str:
        """Insert a single text as a document.

        Args:
            text: Document content.
            metadata: Optional metadata.

        Returns:
            str: The assigned document ID.
        """
        doc = Document(text, metadata=metadata)
        ids = await self.insert_documents([doc])
        return ids[0]

    async def insert_documents(self, docs: list[Document]) -> list[str]:
        """Insert documents with auto-generated IDs and timestamps.

        Args:
            docs: Documents to insert.

        Returns:
            list[str]: Assigned document IDs.
        """
        ids = [self._generate_doc_id() for _ in range(len(docs))]
        timestamp = self.get_timestamp()

        if ids:
            for doc, id in zip(docs, ids):
                doc.metadata["id"] = id
                doc.metadata["timestamp"] = timestamp
                if not doc.metadata.get("area", ""):
                    doc.metadata["area"] = Memory.Area.MAIN.value

            await self.db.insert_documents(docs, ids)
        return ids

    async def update_documents(self, docs: list[Document]) -> list[str]:
        """Update existing documents by ID.

        Args:
            docs: Documents with updated content (must have metadata["id"]).

        Returns:
            list[str]: Updated document IDs.
        """
        ids = [doc.metadata["id"] for doc in docs]
        await self.db.update_documents(docs, ids)
        return ids

    # ── Helpers ──────────────────────────────────────────────────────────

    def _generate_doc_id(self) -> str:
        """Generate a unique document ID."""
        while True:
            doc_id = guids.generate_id(10)
            if not self.db.get_by_ids([doc_id]):
                return doc_id

    @staticmethod
    def _get_comparator(condition: str):
        """Create a metadata filter function from a simpleeval expression.

        Args:
            condition: A simpleeval expression (e.g., "area == 'main'").

        Returns:
            Callable that evaluates the condition against metadata.
        """

        def comparator(data: dict[str, Any]) -> bool:
            try:
                result = simple_eval(condition, names=data)
                return result
            except Exception as e:
                PrintStyle.error(f"Error evaluating condition: {e}")
                return False

        return comparator

    @staticmethod
    def format_docs_plain(docs: list[Document]) -> list[str]:
        """Format documents as plain text with metadata.

        Args:
            docs: Documents to format.

        Returns:
            list[str]: Formatted document strings.
        """
        result = []
        for doc in docs:
            text = ""
            for k, v in doc.metadata.items():
                text += f"{k}: {v}\n"
            text += f"Content: {doc.page_content}"
            result.append(text)
        return result

    @staticmethod
    def get_timestamp() -> str:
        """Get current timestamp string.

        Returns:
            str: Formatted as 'YYYY-MM-DD HH:MM:SS'.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ── Module-level helper functions ────────────────────────────────────────


def get_custom_knowledge_subdir_abs(agent: Agent) -> str:
    """Get absolute path for agent's custom knowledge subdirectory.

    Args:
        agent: The agent instance.

    Returns:
        str: Absolute path to the custom knowledge directory.

    Raises:
        Exception: If no custom knowledge subdir is configured.
    """
    for dir in agent.config.knowledge_subdirs:
        if dir != "default":
            if dir == "custom":
                return files.get_abs_path("usr/knowledge")
            return files.get_abs_path("usr/knowledge", dir)
    raise Exception("No custom knowledge subdir set")


def reload() -> None:
    """Clear the memory index cache, forcing all backends to reload."""
    Memory.index = {}


def abs_db_dir(memory_subdir: str) -> str:
    """Resolve absolute database directory path.

    Args:
        memory_subdir: Memory subdirectory name.

    Returns:
        str: Absolute path to the database directory.
    """
    if memory_subdir.startswith("projects/"):
        from python.helpers.projects import get_project_meta_folder

        return files.get_abs_path(get_project_meta_folder(memory_subdir[9:]), "memory")
    return files.get_abs_path("usr/memory", memory_subdir)


def abs_knowledge_dir(knowledge_subdir: str, *sub_dirs: str) -> str:
    """Resolve absolute knowledge directory path.

    Args:
        knowledge_subdir: Knowledge subdirectory name.
        *sub_dirs: Additional subdirectory components.

    Returns:
        str: Absolute path to the knowledge directory.
    """
    if knowledge_subdir.startswith("projects/"):
        from python.helpers.projects import get_project_meta_folder

        return files.get_abs_path(
            get_project_meta_folder(knowledge_subdir[9:]), "knowledge", *sub_dirs
        )
    if knowledge_subdir == "default":
        return files.get_abs_path("knowledge", *sub_dirs)
    if knowledge_subdir == "custom":
        return files.get_abs_path("usr/knowledge", *sub_dirs)
    return files.get_abs_path("usr/knowledge", knowledge_subdir, *sub_dirs)


def get_memory_subdir_abs(agent: Agent) -> str:
    """Get absolute path for agent's memory subdirectory.

    Args:
        agent: The agent instance.

    Returns:
        str: Absolute path.
    """
    subdir = get_agent_memory_subdir(agent)
    return abs_db_dir(subdir)


def get_agent_memory_subdir(agent: Agent) -> str:
    """Get memory subdirectory for an agent.

    Args:
        agent: The agent instance.

    Returns:
        str: Memory subdirectory name.
    """
    return get_context_memory_subdir(agent.context)


def get_context_memory_subdir(context: AgentContext) -> str:
    """Get memory subdirectory for an agent context.

    Args:
        context: The agent context.

    Returns:
        str: Memory subdirectory name.
    """
    from python.helpers.projects import (
        get_context_memory_subdir as get_project_memory_subdir,
    )

    memory_subdir = get_project_memory_subdir(context)
    if memory_subdir:
        return memory_subdir

    return context.config.memory_subdir or "default"


def get_existing_memory_subdirs() -> list[str]:
    """List all existing memory subdirectories.

    Returns:
        list[str]: Memory subdirectory names (always includes 'default').
    """
    try:
        from python.helpers.projects import (
            get_project_meta_folder,
            get_projects_parent_folder,
        )

        subdirs = files.get_subdirectories("usr/memory")

        project_subdirs = files.get_subdirectories(get_projects_parent_folder())
        for project_subdir in project_subdirs:
            # Check for either FAISS or SQLite index files
            has_faiss = files.exists(
                get_project_meta_folder(project_subdir), "memory", "index.faiss"
            )
            has_sqlite = files.exists(
                get_project_meta_folder(project_subdir), "memory", "memory.db"
            )
            if has_faiss or has_sqlite:
                subdirs.append(f"projects/{project_subdir}")

        if "default" not in subdirs:
            subdirs.insert(0, "default")

        return subdirs
    except Exception as e:
        PrintStyle.error(f"Failed to get memory subdirectories: {str(e)}")
        return ["default"]


def get_knowledge_subdirs_by_memory_subdir(
    memory_subdir: str, default: list[str]
) -> list[str]:
    """Get knowledge subdirectories associated with a memory subdirectory.

    Args:
        memory_subdir: Memory subdirectory name.
        default: Default knowledge subdirectories.

    Returns:
        list[str]: Knowledge subdirectories.
    """
    if memory_subdir.startswith("projects/"):
        from python.helpers.projects import get_project_meta_folder

        default.append(get_project_meta_folder(memory_subdir[9:], "knowledge"))
    return default
