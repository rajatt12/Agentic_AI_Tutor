
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.embeddings import EmbeddingManager

class RetrieverAgent:
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
    
    def retrieve_content(self, query, topic=None):
        """Retrieve relevant study materials based on query"""
        
        documents, metadata = self.embedding_manager.search(query, n_results=3)
        
        
        retrieved_content = "\n\n".join([
            f"**Source {i+1}:** {doc}" 
            for i, doc in enumerate(documents)
        ])
        
        return {
            "retrieved_content": retrieved_content,
            "sources": metadata
        }
