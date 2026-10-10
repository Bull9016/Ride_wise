import os
import glob
import logging
from typing import List, Dict

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    """
    Handles unstructured data (PDFs).
    Uses FAISS and HuggingFace local embeddings to perform RAG.
    """
    def __init__(self, data_dir: str = "data/"):
        self.data_dir = data_dir
        self.vector_store_path = os.path.join(data_dir, "faiss_index")
        
        # Load local embeddings model to comply with 'no other LLMs/API keys' rule
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None

    def initialize_index(self):
        """Loads PDFs, chunks them, and builds or loads the FAISS index."""
        if os.path.exists(self.vector_store_path):
            logger.info("Loading existing FAISS index...")
            self.vector_store = FAISS.load_local(
                self.vector_store_path, 
                self.embeddings,
                allow_dangerous_deserialization=True # Required for FAISS locally
            )
        else:
            logger.info("Building new FAISS index from PDFs...")
            docs = []
            pdf_files = glob.glob(os.path.join(self.data_dir, "*.pdf"))
            
            for pdf_file in pdf_files:
                loader = PyPDFLoader(pdf_file)
                docs.extend(loader.load())
                
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            splits = text_splitter.split_documents(docs)
            
            self.vector_store = FAISS.from_documents(splits, self.embeddings)
            self.vector_store.save_local(self.vector_store_path)
            logger.info("FAISS index built and saved.")

    def search_policies(self, query: str, top_k: int = 3) -> str:
        """
        Searches the FAISS index and returns a concatenated string of results.
        """
        if not self.vector_store:
            self.initialize_index()
            
        results = self.vector_store.similarity_search(query, k=top_k)
        
        # Format the output clearly for the LLM
        formatted_results = "\n\n".join([f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}" for doc in results])
        return formatted_results if formatted_results else "No relevant policy documents found."
