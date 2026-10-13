import sys

from app.rag.retriever import _search_policy_docs

query = " ".join(sys.argv[1:]) or "can a junior do authentication changes"

for rank, doc in enumerate(_search_policy_docs(query, 6), start=1):
    score = doc["metadata"]["score"]
    print(f"{rank}  {score:.3f}  {doc['page_content'][:90]}")