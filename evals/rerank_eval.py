import json
from pathlib import Path

from fastembed.rerank.cross_encoder import TextCrossEncoder

from app.rag.retriever import _search_policy_docs
from evals.metrics import find_rank, recall_at_k, reciprocal_rank

K = 3
WIDE_NET = 19 
MODEL = "Xenova/ms-marco-MiniLM-L-6-v2"
GOLDEN_PATH = Path(__file__).parent / "golden_set.json"

reranker = TextCrossEncoder(model_name=MODEL)


def rerank(query: str, docs: list[dict]) -> list[tuple[str, float]]:
    texts = [d["page_content"] for d in docs]
    scores = list(reranker.rerank(query, texts))
    pairs = list(zip(texts, scores))
    pairs.sort(key=lambda p: p[1], reverse=True)
    return pairs


def main():
    questions = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    recalls, rrs = [], []

    print(f"{'ID':<4}{'RANK':<8}{'RR':<7}QUESTION")
    for item in questions:
        docs = _search_policy_docs(item["question"], WIDE_NET)
        ranked = rerank(item["question"], docs)
        texts = [text for text, _ in ranked]

        rank = find_rank(texts, item["expected"])
        recalls.append(recall_at_k(rank, K))
        rrs.append(reciprocal_rank(rank))

        shown = rank if rank is not None else "miss"
        print(f"{item['id']:<4}{str(shown):<8}{rrs[-1]:<7.2f}{item['question']}")

    print()
    print(f"Model:     {MODEL}")
    print(f"Recall@{K}: {sum(recalls) / len(recalls):.2f}")
    print(f"MRR:       {sum(rrs) / len(rrs):.2f}")


if __name__ == "__main__":
    main()