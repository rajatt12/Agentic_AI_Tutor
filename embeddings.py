from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

class EmbeddingManager:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        
        self.client = chromadb.PersistentClient(path="./database/vector_store")
        
        self.collection = self.client.get_or_create_collection(
            name="study_materials",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, documents, metadata):
        """Add study materials to vector database"""
        embeddings = self.model.encode(documents)
        
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadata,
            ids=[f"doc_{i}" for i in range(len(documents))]
        )
    
    def search(self, query, n_results=3):
        """Search for relevant study materials"""
        query_embedding = self.model.encode([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )
        
        return results['documents'][0], results['metadatas'][0]
