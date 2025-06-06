from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

index_path = Path("faiss_index")
embedding = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

def save_to_vectorstore(docs: list[Document]):
    if not docs:
        raise ValueError("No valid documents to embed in vector store.")
    db = FAISS.from_documents(docs, embedding)
    db.save_local(str(index_path))

def load_vectorstore():
    if not index_path.exists():
        return None
    # Add allow_dangerous_deserialization=True since we trust our own files
    return FAISS.load_local(
        folder_path=str(index_path),
        embeddings=embedding,
        allow_dangerous_deserialization=True
    )