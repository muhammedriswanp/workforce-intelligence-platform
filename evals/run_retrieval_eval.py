import json
from pathlib import Path
import sys
from app.rag.retriever import retrieve_relevant_policies
from evals.metrics import find_rank, recall_at_k, reciprocal_rank

K = 3
GOLDEN_PATH = Path(__file__).parent / "golden_set.json"


def main():
    questions = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))

    recalls = []
    rrs = []

    print(f"{'ID':<4}{'RANK':<8}{'RR':<7}QUESTION")
    for item in questions:
        retrieved = retrieve_relevant_policies(item["question"], k=K)
        rank = find_rank(retrieved, item["expected"])

        recalls.append(recall_at_k(rank, K))
        rrs.append(reciprocal_rank(rank))

        shown_rank = rank if rank is not None else "miss"
        print(f"{item['id']:<4}{str(shown_rank):<8}{rrs[-1]:<7.2f}{item['question']}")

    print()
    recall = sum(recalls) / len(recalls)
    mrr = sum(rrs) / len(rrs)
    print(f"Recall@{K}: {recall:.2f}")
    print(f"MRR:       {mrr:.2f}")

    if recall < 0.90 or mrr < 0.90:
        print("FAILED: retrieval quality dropped below the threshold")
        sys.exit(1)