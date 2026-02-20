# RubyRAG class for document processing and retrieval using FAISS.
import os
from dotenv import load_dotenv
from typing import List, Optional

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()

class RubyRAG:
    """
    RubyRAG class for document processing and retrieval using FAISS.

    Args:
        db_path (str): Path to the FAISS database.
        embedding_model (str): Embedding model to use.
        chunk_size (int): Size of text chunks.
        chunk_overlap (int): Overlap between text chunks.
    
    usage:
        rag = RubyRAG()
        rag.add_documents("docs/knowledge.pdf")
        response = rag.query("What is the main topic?")
        print(response)
    """
    def __init__(
        self,
        db_path: str = "ruby_rag/db",
        embedding_model: str = "text-embedding-3-small",
        chunk_size: int = 600,
        chunk_overlap: int = 80,
        
    ):

        self.db_path = db_path # Path to the FAISS database
        self.embedding_model = OpenAIEmbeddings(model=embedding_model) # Embedding model to use
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap)
        self.vectorstore = None # FAISS vector store
        # Load existing DB if present
        if os.path.exists(db_path):
            print(f"Loading FAISS DB from {db_path}")
            self.vectorstore = FAISS.load_local(
                db_path,
                self.embedding_model,
                allow_dangerous_deserialization=True,
            )
        else:
            print("No existing DB found. New DB will be created.")
    


    def _load_documents(self, file_path: str) -> List[Document]:
        """
        Load documents from a file.

        Args:
            file_path (str): Path to the document file.

        Returns:
            List[Document]: List of documents loaded from the file.
        """
        ext = os.path.splitext(file_path)[-1].lower()

        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding="utf-8")

        docs = loader.load()
        return self.text_splitter.split_documents(docs)
    
    def add_documents(self, file_path: str):
        """
        Add documents to the FAISS vector store.

        Args:
            file_path (str): Path to the document file.
        """
        docs = self._load_documents(file_path)
        if self.vectorstore is None:
            print("Creating new FAISS DB")
            self.vectorstore = FAISS.from_documents(
                docs,
                self.embedding_model,
            )
        else:
            print("Adding documents to existing FAISS DB")
            self.vectorstore.add_documents(docs)
        
        self.vectorstore.save_local(self.db_path)
        print(f"Documents added to FAISS DB at {self.db_path}")

    def query(self, query: str, k: int = 3) -> str:
        """
        Query the FAISS vector store.

        Args:
            query (str): Query to search for.
            k (int): Number of documents to return.

        Returns:
            str: Query response.
        """
        if self.vectorstore is None:
            raise RuntimeError("No existing DB found.")

        docs = self.vectorstore.similarity_search(query, k=k)

        context = []
        for i, doc in enumerate(docs, 1):
            context.append(
                f"[Context {i}]\n{doc.page_content}"
            )

        return "\n\n---\n\n".join(context)
