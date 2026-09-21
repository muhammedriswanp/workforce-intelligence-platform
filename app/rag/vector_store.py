from dotenv import load_dotenv
import os
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "workforce-policies")

embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

def get_vector_store() -> PineconeVectorStore:
    return PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings,
        pinecone_api_key=PINECONE_API_KEY,
    )

