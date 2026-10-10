import logging
from datetime import datetime

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore

from app.rag.vector_store import embeddings, PINECONE_API_KEY, PINECONE_INDEX_NAME

logger = logging.getLogger(__name__)

SPRINT_NAMESPACE = "sprint-updates"


def get_sprint_vector_store() -> PineconeVectorStore:
    return PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings,
        pinecone_api_key=PINECONE_API_KEY,
        namespace=SPRINT_NAMESPACE,
    )


def index_sprint_update(
    update_id: int,
    employee_id: int,
    task_id: int,
    update_text: str,
    created_at: datetime,
) -> None:
    """Copy one sprint update from PostgreSQL into Pinecone.
    Never raises: PostgreSQL is the real record, so a Pinecone failure is only logged."""
    try:
        document = Document(
            page_content=update_text,
            metadata={
                "update_id": update_id,
                "employee_id": employee_id,
                "task_id": task_id,
                "created_at": created_at.isoformat(),
            },
        )
        get_sprint_vector_store().add_documents(
            [document], ids=[f"sprint-{update_id}"]
        )
    except Exception:
        logger.exception("Failed to index sprint update %s in Pinecone", update_id)