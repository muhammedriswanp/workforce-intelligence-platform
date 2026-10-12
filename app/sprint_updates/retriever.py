import logging
from datetime import datetime, timedelta

from app.rag.vector_store import get_vector_store
from app.sprint_updates.vector_service import SPRINT_NAMESPACE

logger = logging.getLogger(__name__)


def get_recent_sprint_updates(
    employee_id: int, query: str, days: int = 14, limit: int = 2
) -> list[str]:
    """Return up to `limit` recent sprint updates of ONE employee,
    most relevant to `query`. Returns [] if there are none or Pinecone fails."""
    try:
        store = get_vector_store(namespace=SPRINT_NAMESPACE)
        docs = store.similarity_search(
            query, k=6, filter={"employee_id": employee_id}
        )
    except Exception:
        logger.exception("Sprint update search failed for employee %s", employee_id)
        return []

    cutoff = datetime.utcnow() - timedelta(days=days)
    recent = []
    for doc in docs:
        try:
            created = datetime.fromisoformat(doc.metadata["created_at"])
        except (KeyError, ValueError):
            continue
        if created >= cutoff:
            recent.append((created, doc.page_content[:300]))

    recent.sort(key=lambda item: item[0], reverse=True)  # newest first
    return [f"{created:%Y-%m-%d}: {text}" for created, text in recent[:limit]]