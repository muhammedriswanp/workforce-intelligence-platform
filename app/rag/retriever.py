from app.rag.vector_store import get_vector_store
from langsmith import traceable


@traceable(run_type="retriever", name="policy_retrieval")
def _search_policy_docs(query: str, k: int):
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_score(query, k=k)
    return [
        {
            "page_content": doc.page_content,
            "metadata": {**doc.metadata, "score": float(score)},
        }
        for doc, score in results
    ]


def retrieve_relevant_policies(query: str, k: int = 3) -> list[str]:
    docs = _search_policy_docs(query, k)
    return [d["page_content"] for d in docs]