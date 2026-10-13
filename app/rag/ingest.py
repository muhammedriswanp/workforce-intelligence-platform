import os
import sys
import hashlib
from langchain_core.documents import Document
from app.rag.vector_store import get_vector_store

KNOWLEDGE_DIR = os.path.join("app", "rag", "knowledge")

FILES = [
    ("assignment_policies.txt", "workforce_policy"),
    ("role_guidelines.txt", "role_guideline"),
    ("project_standards.txt", "project_standard"),
    ("hr_policies.txt", "hr_policy"),
]


def make_id(filename: str, line: str) -> str:
    """Same file + same line always gives the same ID, so re-running
    overwrites the record instead of creating a duplicate."""
    return hashlib.sha1(f"{filename}:{line}".encode("utf-8")).hexdigest()


def ingest_knowledge_base(reset: bool = False):
    """Reads policy text files and uploads embeddings to Pinecone."""
    documents = []
    ids = []
    for filename, category in FILES:
        filepath = os.path.join(KNOWLEDGE_DIR, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            lines = lines = [
                line.strip()
                for line in f
                if line.strip().startswith("- ")
            ]

        for line in lines:
            documents.append(
                Document(
                    page_content=line,
                    metadata={"source": filename, "category": category},
                )
            )
            ids.append(make_id(filename, line))

    if not documents:
        print("No documents found to index.")
        return

    vector_store = get_vector_store()  # default namespace = policies only

    if reset:
        print("Deleting all records in the default (policy) namespace...")
        vector_store.delete(delete_all=True)

    print(f"Uploading {len(documents)} policy rules to Pinecone...")
    vector_store.add_documents(documents, ids=ids)
    print("Pinecone ingestion complete!")


if __name__ == "__main__":
    ingest_knowledge_base(reset="--reset" in sys.argv)