import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.embeddings import EmbeddingManager

class RetrieverAgent:
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
    
    def retrieve_content(self, query, topic=None, search_mode="hybrid"):
        """
        Retrieve relevant study materials based on query.
        Supports search_mode: 'hybrid' (BM25 + Dense Vector), 'dense', or 'bm25'.
        """
        if search_mode == "bm25":
            documents, metadata = self.embedding_manager.search_bm25(query, n_results=3)
        elif search_mode == "dense":
            documents, metadata = self.embedding_manager.search_dense(query, n_results=3)
        else:
            documents, metadata = self.embedding_manager.hybrid_search(query, n_results=3)
        
        if not documents:
            return {
                "retrieved_content": "",
                "sources": []
            }
        
        sources_formatted = []
        for i, (doc, meta) in enumerate(zip(documents, metadata)):
            match_type = meta.get("match_type", "relevant")
            sources_formatted.append(f"**Source {i+1} [{match_type.upper()}]:** {doc}")

        retrieved_content = "\n\n".join(sources_formatted)
        
        return {
            "retrieved_content": retrieved_content,
            "sources": metadata
        }
