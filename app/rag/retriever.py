from app.rag.vector_store import get_vector_store

def retrieve_relevant_policies(query: str, k: int = 3)-> list[str]:
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=k)
    return [doc.page_content for doc in results]