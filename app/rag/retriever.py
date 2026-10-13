from functools import lru_cache

from fastembed.rerank.cross_encoder import TextCrossEncoder
from langsmith import traceable

from app.rag.vector_store import get_vector_store

RERANK_MODEL = "Xenova/ms-marco-MiniLM-L-6-v2"
WIDE_NET = 20 

@lru_cache(maxsize=1)
def _get_reranker() -> TextCrossEncoder:
    # Loaded once, on first use, then reused for every question.
    return TextCrossEncoder(model_name=RERANK_MODEL)


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


@traceable(run_type="retriever", name="policy_rerank")
def _rerank_docs(query: str, docs: list[dict], k: int):
    if not docs:
        return []
    texts = [d["page_content"] for d in docs]
    scores = list(_get_reranker().rerank(query, texts))
    ranked = sorted(zip(docs, scores), key=lambda p: p[1], reverse=True)
    return [
        {
            "page_content": doc["page_content"],
            "metadata": {**doc["metadata"], "rerank_score": float(score)},
        }
        for doc, score in ranked[:k]
    ]


def retrieve_relevant_policies(query: str, k: int = 3) -> list[str]:
    docs = _search_policy_docs(query, max(WIDE_NET, k))
    top = _rerank_docs(query, docs, k)
    return [d["page_content"] for d in top]