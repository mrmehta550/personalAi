import os
import sys

# Ensure backend root directory is in sys.path when running `python app/seed/seed_ingest.py` directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import argparse
from langchain_core.documents import Document
from app.vectorstore.collection_manager import collection_manager
from app.ingest.splitter import split_documents
from app.core.config import settings
from app.core.logger import logger


def _item_to_text(item) -> str:
    """
    Convert a seed data item to a plain text string suitable for embedding.

    Handles multiple data shapes:
    - str  → returned as-is
    - dict with "question" + "answer" keys → formatted as Q&A text
    - dict with "text" key → returns the text value
    - dict (generic) → key: value pairs joined as text
    """
    if isinstance(item, str):
        return item.strip()

    if isinstance(item, dict):
        # FAQ-style: {question, answer}
        if "question" in item and "answer" in item:
            return f"Q: {item['question']}\nA: {item['answer']}"

        # Text-only shorthand: {text: "..."}
        if "text" in item:
            return str(item["text"]).strip()

        # Generic dict: join all non-empty key-value pairs
        parts = []
        for k, v in item.items():
            if v and str(v).strip():
                label = k.replace("_", " ").title()
                parts.append(f"{label}: {v}")
        return "\n".join(parts)

    # Fallback
    return str(item).strip()


def seed_knowledge_base(force: bool = False, reset: bool = False):
    """
    Populates ChromaDB with seed portfolio data across all collections.

    Args:
        force: If True, re-seeds even if collections already have data.
        reset: If True, deletes all existing collections first, then re-creates and seeds.
    """
    if reset:
        logger.info("RESET flag passed: Deleting all existing ChromaDB collections...")
        for col_name in settings.COLLECTIONS:
            try:
                collection_manager.chroma_client.delete_collection(col_name)
                logger.info(f"  Deleted Chroma collection '{col_name}'")
            except Exception as e:
                logger.debug(f"  Collection '{col_name}' did not exist or could not be deleted: {e}")

    elif not force:
        stats = collection_manager.get_collection_stats()
        total_existing = sum(stats.values())
        if total_existing > 0:
            logger.info(
                f"Knowledge base already seeded ({total_existing} total vectors). "
                "Skipping. Pass --reset or --force to re-seed."
            )
            return

    json_path = os.path.join(os.path.dirname(__file__), "seed_data.json")
    if not os.path.exists(json_path):
        logger.warning(f"Seed data file not found at {json_path}")
        return

    logger.info("Seeding portfolio knowledge base into ChromaDB...")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_chunks = 0

    for col_name, items in data.items():
        if not items:
            logger.warning(f"  Collection '{col_name}' is empty in seed_data.json - skipping.")
            continue

        docs = []
        for idx, item in enumerate(items):
            # Convert each item (str or dict) to a human-readable text string
            text = _item_to_text(item)
            if not text:
                continue

            # Determine source label for metadata
            if isinstance(item, dict):
                source = (
                    item.get("source", None)
                    or item.get("name", None)
                    or item.get("question", f"item_{idx}")
                )
            else:
                source = f"item_{idx}"

            docs.append(Document(
                page_content=text,
                metadata={
                    "source_file": "seed_data.json",
                    "source": str(source),
                    "item_idx": idx,
                    "collection": col_name,
                }
            ))

        if not docs:
            continue

        chunks = split_documents(docs, collection_name=col_name, chunk_size=400, chunk_overlap=40)
        collection_manager.add_documents(col_name, chunks)
        total_chunks += len(chunks)
        logger.info(f"  Seeded collection '{col_name}': {len(docs)} items -> {len(chunks)} chunks")

    # Final Verification Step
    stats = collection_manager.get_collection_stats()
    logger.info(f"Knowledge base seeding complete. Total chunks ingested: {total_chunks}")
    logger.info(f"Collection Document Counts: {stats}")

    # Check that NO Alex Morgan or fictional identity documents exist in ChromaDB
    verify_no_fictional_data()


def verify_no_fictional_data():
    """Verifies that no fictional Alex Morgan or TechCorp documents exist in ChromaDB."""
    fictional_terms = ["Alex Morgan", "alexmorgan", "TechCorp", "DataScale", "Stanford University"]
    found_violations = []

    for col_name in settings.COLLECTIONS:
        try:
            col = collection_manager.chroma_client.get_collection(col_name)
            all_docs = col.get()
            for doc_text in all_docs.get("documents", []):
                for term in fictional_terms:
                    if term.lower() in doc_text.lower():
                        found_violations.append((col_name, term, doc_text[:100]))
        except Exception as e:
            logger.debug(f"Error checking collection '{col_name}': {e}")

    if found_violations:
        logger.error(f"VERIFICATION FAILED! Fictional documents found in ChromaDB: {found_violations}")
        raise ValueError(f"Fictional data detected in ChromaDB: {found_violations}")
    else:
        logger.info("[VERIFICATION PASSED] Zero fictional documents found in ChromaDB.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed portfolio data into ChromaDB")
    parser.add_argument("--reset", action="store_true", help="Delete existing collections and re-seed from scratch")
    parser.add_argument("--force", action="store_true", help="Force re-seed without deleting existing collections")
    args = parser.parse_args()

    seed_knowledge_base(force=args.force, reset=args.reset)
