import os
from typing import List
from dotenv import load_dotenv

load_dotenv()
from langchain_community.document_loaders import TextLoader, DirectoryLoader, PyPDFLoader
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Define base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

def ingest_documents():
    """
    Ingests documents from backend/data/raw. 
    Supports .txt and .pdf files.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created {DATA_DIR}. Please add documents.")
        return

    documents: List[Document] = []

    # 1. Load Text Files
    try:
        txt_loader = DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader)
        txt_docs = txt_loader.load()
        print(f"Loaded {len(txt_docs)} text documents.")
        documents.extend(txt_docs)
    except Exception as e:
        print(f"Error loading text files: {e}")

    # 2. Load PDF Files
    try:
        # DirectoryLoader for PDFs
        pdf_loader = DirectoryLoader(DATA_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader)
        pdf_docs = pdf_loader.load()
        print(f"Loaded {len(pdf_docs)} PDF documents.")
        documents.extend(pdf_docs)
    except Exception as e:
        print(f"Error loading PDF files: {e}")

    if not documents:
        print("No documents found to ingest.")
        return

    # 3. Split Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    # Add metadata for source type if needed
    for doc in documents:
        source = doc.metadata.get("source", "")
        if source.endswith(".pdf"):
             doc.metadata["type"] = "Academic/Written"
        else:
             doc.metadata["type"] = "General/Oral"

    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    # 4. Embed and Store
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        persist_directory=DB_DIR, 
        embedding_function=embeddings
    )
    
    vectorstore.add_documents(chunks)
    vectorstore.persist()
    print("Ingestion complete. Database updated.")

if __name__ == "__main__":
    ingest_documents()
