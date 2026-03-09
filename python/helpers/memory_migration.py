"""Migration tool for converting FAISS memory databases to SQLite.

Reads an existing FAISS index and re-inserts all documents into a new
SQLite backend with fresh embeddings.

Usage:
    python -m python.helpers.memory_migration [--subdir default] [--all]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import models
from python.helpers.memory import abs_db_dir, get_existing_memory_subdirs
from python.helpers.print_style import PrintStyle


def migrate_subdir(memory_subdir: str, model_config: models.ModelConfig) -> dict:
    """Migrate a single memory subdirectory from FAISS to SQLite.

    Args:
        memory_subdir: Memory subdirectory name (e.g., 'default').
        model_config: Embedding model configuration.

    Returns:
        dict: Migration result with doc_count, status, errors.
    """

    db_dir = abs_db_dir(memory_subdir)
    faiss_index_path = os.path.join(db_dir, "index.faiss")

    if not os.path.exists(faiss_index_path):
        return {
            "subdir": memory_subdir,
            "status": "skipped",
            "reason": "No FAISS index found",
            "doc_count": 0,
        }

    PrintStyle.standard(f"Migrating '{memory_subdir}' from FAISS to SQLite...")

    # Load FAISS index
    from python.helpers.memory_faiss import FAISSMemoryBackend

    faiss_backend, _ = FAISSMemoryBackend.initialize(
        model_config=model_config,
        db_dir=db_dir,
        in_memory=False,
    )

    all_docs = faiss_backend.get_all_docs()
    doc_count = len(all_docs)

    if doc_count == 0:
        return {
            "subdir": memory_subdir,
            "status": "skipped",
            "reason": "FAISS index is empty",
            "doc_count": 0,
        }

    PrintStyle.standard(f"  Found {doc_count} documents to migrate")

    # Initialize SQLite backend
    from python.helpers.memory_sqlite import SQLiteMemoryBackend

    sqlite_backend, _ = SQLiteMemoryBackend.initialize(
        model_config=model_config,
        db_dir=db_dir,
        in_memory=False,
    )

    # Insert all documents
    doc_list = list(all_docs.values())
    id_list = list(all_docs.keys())

    batch_size = 50
    migrated = 0
    errors = 0

    for i in range(0, len(doc_list), batch_size):
        batch_docs = doc_list[i : i + batch_size]
        batch_ids = id_list[i : i + batch_size]
        try:
            sqlite_backend.add_documents_sync(batch_docs, batch_ids)
            migrated += len(batch_docs)
            PrintStyle.standard(f"  Migrated {migrated}/{doc_count} documents...")
        except Exception as e:
            errors += len(batch_docs)
            PrintStyle.error(f"  Error migrating batch {i}: {e}")

    # Preserve knowledge import index
    ki_path = os.path.join(db_dir, "knowledge_import.json")
    if os.path.exists(ki_path):
        PrintStyle.standard("  Preserved knowledge_import.json")

    result = {
        "subdir": memory_subdir,
        "status": "success" if errors == 0 else "partial",
        "doc_count": migrated,
        "errors": errors,
    }

    PrintStyle.standard(
        f"  Migration complete: {migrated} docs migrated, {errors} errors"
    )
    return result


def migrate_all(model_config: models.ModelConfig) -> list[dict]:
    """Migrate all existing memory subdirectories.

    Args:
        model_config: Embedding model configuration.

    Returns:
        list[dict]: Results for each subdirectory.
    """
    subdirs = get_existing_memory_subdirs()
    results = []

    for subdir in subdirs:
        result = migrate_subdir(subdir, model_config)
        results.append(result)

    return results


def main() -> None:
    """CLI entry point for migration."""
    parser = argparse.ArgumentParser(
        description="Migrate Agent Zero memory from FAISS to SQLite"
    )
    parser.add_argument(
        "--subdir",
        default=None,
        help="Memory subdirectory to migrate (default: all)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Migrate all memory subdirectories",
    )
    args = parser.parse_args()

    # Initialize config to get embedding model
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    import initialize

    agent_config = initialize.initialize_agent()
    model_config = agent_config.embeddings_model

    if args.subdir:
        result = migrate_subdir(args.subdir, model_config)
        PrintStyle.standard(f"\nResult: {json.dumps(result, indent=2)}")
    else:
        results = migrate_all(model_config)
        PrintStyle.standard(f"\nResults: {json.dumps(results, indent=2)}")

        total = sum(r["doc_count"] for r in results)
        errors = sum(r.get("errors", 0) for r in results)
        PrintStyle.standard(f"\nTotal: {total} documents migrated, {errors} errors")


if __name__ == "__main__":
    main()
