import os 
from langchain_core.documents import Document
from app.rag.vector_store import get_vector_store

KNOWLEDGE_DIR = os.path.join("app", "rag", "knowledge")

def ingest_knowledge_base():
    """Reads policy text files and uploads embeddings to Pinecone."""
    files = [
        ("assignment_policies.txt", "workforce_policy"),
        ("role_guidelines.txt", "role_guideline"),
        ("project_standards.txt", "project_standard"),
    ]

    documents = []
    for filename, category in files:
        filepath = os.path.join(KNOWLEDGE_DIR, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        for line in lines:
            documents.append(
                Document(
                    page_content=line,
                    metadata={"source": filename, "category": category},
                )
            )

    if not documents:
        print("No documents found to index.")
        return

    print(f"Uploading {len(documents)} policy rules to Pinecone...")
    vector_store = get_vector_store()
    vector_store.add_documents(documents)
    print("Pinecone ingestion complete!")


if __name__ == "__main__":
    ingest_knowledge_base()