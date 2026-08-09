from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from app.vectorstore.chroma_client import get_chroma_client
from app.vectorstore.embeddings import get_embedding_model
from app.core.config import settings
from app.core.logger import logger


# ─── Project name → canonical label (for filtering) ─────────────────────────

_PROJECT_ALIASES = {
    "ai mail automation": [
        "ai mail automation",
        "mail automation",
        "email automation",
        "ai email automation",
        "ai mail",
        "email assistant",
        "mail assistant"
    ],

    "youtube ai assistant": [
        "youtube ai assistant",
        "youtube assistant",
        "youtube ai",
        "youtube project"
    ],

    "student portal": [
        "student portal",
        "student management",
        "school portal"
    ],

    "personal ai assistant": [
        "personal ai assistant",
        "digital twin",
        "portfolio assistant",
        "personal ai",
        "ai portfolio assistant"
    ]
}
# Minimum relevance score to accept a chunk (cosine similarity, 0–1 scale)
_RELEVANCE_THRESHOLD = 0.20


def _detect_project_in_query(query_lower: str) -> Optional[str]:
    """
    Returns the canonical project label if the query targets a specific project,
    or None if it's a general query.
    """
    for canonical, aliases in _PROJECT_ALIASES.items():
        for alias in aliases:
            if alias in query_lower:
                return canonical
    return None


class CollectionManager:
    def __init__(self):
        self.chroma_client = get_chroma_client()
        self.embedding_model = get_embedding_model()

    def get_vectorstore(self, collection_name: str) -> Chroma:
        if collection_name not in settings.COLLECTIONS:
            collection_name = "about_me"
        return Chroma(
            client=self.chroma_client,
            collection_name=collection_name,
            embedding_function=self.embedding_model
        )

    def search_collections(
        self,
        query: str,
        collection_names: List[str],
        top_k: int = 3,
        use_mmr: bool = True
    ) -> List[Dict[str, Any]]:

        results = []

        if not collection_names:
            return []

        valid_collections = [
            c for c in collection_names
            if c in settings.COLLECTIONS
        ]

        if not valid_collections:
            return []

        query_lower = query.lower().strip()

        # Detect if the query is about a specific known project
        specific_project = _detect_project_in_query(query_lower)

        # Detect project-count / overview questions
        _COUNT_PHRASES = [
            "how many projects",
            "number of projects",
            "total projects",
            "how many project",
            "projects have you built",
            "projects have you done",
            "projects did you build",
            "what projects",
            "tell me about your projects",
            "list your projects",
        ]
        is_project_count_query = any(phrase in query_lower for phrase in _COUNT_PHRASES)

        # ── Search each collection ────────────────────────────────────────────
        for col_name in valid_collections:
            try:
                vs = self.get_vectorstore(col_name)

                # Determine how many chunks to fetch per collection
                if col_name == "projects" and is_project_count_query:
                    k = 6   # fetch more to see all projects
                elif col_name == "projects" and specific_project:
                    k = 3
                else:
                    k = top_k

                # Similarity search with relevance scores
                docs_with_scores = vs.similarity_search_with_relevance_scores(
                    query, k=k
                )

                for doc, score in docs_with_scores:
                    content = doc.page_content.strip()

                    if not content:
                        continue

                    # Drop clearly irrelevant chunks
                    if score < _RELEVANCE_THRESHOLD:
                        logger.debug(
                            f"Dropped low-score chunk [{col_name}] "
                            f"score={score:.3f}: {content[:60]}"
                        )
                        continue

                    # ── Project-specific chunk filtering ─────────────────────
                    # When the user asks about a specific project, only keep
                    # chunks from the `projects` collection that mention it.
                    if col_name == "projects" and specific_project:
                        aliases = _PROJECT_ALIASES.get(specific_project, [specific_project])
                        if not any(alias in content.lower() for alias in aliases):
                            logger.debug(
                                f"Filtered irrelevant projects chunk "
                                f"(not about {specific_project}): {content[:60]}"
                            )
                            continue

                    results.append({
                        "content": content,
                        "score": float(score),
                        "metadata": {
                            **doc.metadata,
                            "collection": col_name,
                            "relevance_score": float(score),
                        }
                    })

            except Exception as e:
                logger.error(f"Error searching collection {col_name}: {e}")

        # ── Deduplicate ───────────────────────────────────────────────────────
        seen: set = set()
        unique_results: List[Dict[str, Any]] = []
        for result in results:
            key = result["content"].strip()
            if key in seen:
                continue
            seen.add(key)
            unique_results.append(result)

        # ── Sort by relevance descending ──────────────────────────────────────
        unique_results.sort(key=lambda x: x["score"], reverse=True)

        # ── Apply final cap ───────────────────────────────────────────────────
        max_results = 6 if is_project_count_query else 4
        final_results = unique_results[:max_results]

        logger.info(
            f"Returning {len(final_results)} chunks from {valid_collections} "
            f"(specific_project={specific_project}, count_query={is_project_count_query})"
        )
        for r in final_results:
            logger.info(
                f"  [{r['metadata']['collection']}] score={r['score']:.3f} "
                f"src={r['metadata'].get('source', 'unknown')}"
            )

        return final_results

    def add_documents(self, collection_name: str, documents: List[Document]) -> int:
        if collection_name not in settings.COLLECTIONS:
            raise ValueError(
                f"Collection '{collection_name}' is not in configured collections."
            )
        vs = self.get_vectorstore(collection_name)
        vs.add_documents(documents)
        logger.info(f"Added {len(documents)} documents to Chroma collection '{collection_name}'")
        return len(documents)

    def get_collection_stats(self) -> Dict[str, int]:
        stats = {}
        for col_name in settings.COLLECTIONS:
            try:
                col = self.chroma_client.get_collection(col_name)
                stats[col_name] = col.count()
            except Exception:
                stats[col_name] = 0
        return stats


collection_manager = CollectionManager()
