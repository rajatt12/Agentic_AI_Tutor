import re
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

class EmbeddingManager:
    def __init__(self, collection_name="study_materials", db_path="./database/vector_store"):
        """Initialize EmbeddingManager with ChromaDB (HNSW) and BM25 Lexical Index"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path=db_path)
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # In-memory document storage for BM25
        self.documents = []
        self.metadatas = []
        self.doc_ids = []
        self.bm25 = None
        
        # Load existing documents into BM25 if ChromaDB has data
        self._sync_bm25_from_chroma()

    def _tokenize(self, text):
        """Simple, robust tokenization for BM25 (words, numbers, symbols)"""
        return re.findall(r'\b\w+\b|[^\w\s]', text.lower())

    def _sync_bm25_from_chroma(self):
        """Sync existing ChromaDB documents to the in-memory BM25 index"""
        try:
            stored = self.collection.get()
            if stored and stored.get('documents'):
                self.documents = stored['documents']
                self.metadatas = stored.get('metadatas', [{} for _ in self.documents])
                self.doc_ids = stored.get('ids', [f"doc_{i}" for i in range(len(self.documents))])
                
                tokenized_corpus = [self._tokenize(doc) for doc in self.documents]
                if tokenized_corpus:
                    self.bm25 = BM25Okapi(tokenized_corpus)
        except Exception as e:
            print(f"Warning: Could not sync BM25 index from ChromaDB: {e}")

    def add_documents(self, documents, metadata=None):
        """Add study materials to both ChromaDB (Dense) and BM25 (Sparse) indexes"""
        if not documents:
            return
        
        if metadata is None:
            metadata = [{} for _ in documents]

        embeddings = self.model.encode(documents)
        start_idx = len(self.documents)
        new_ids = [f"doc_{start_idx + i}" for i in range(len(documents))]

        # 1. Add to ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadata,
            ids=new_ids
        )

        # 2. Update BM25 index
        self.documents.extend(documents)
        self.metadatas.extend(metadata)
        self.doc_ids.extend(new_ids)
        
        tokenized_corpus = [self._tokenize(doc) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search_dense(self, query, n_results=3):
        """Dense semantic search using ChromaDB (HNSW + Cosine Distance)"""
        try:
            count = self.collection.count()
            if count == 0:
                return [], []
            
            n_results = min(n_results, count)
            query_embedding = self.model.encode([query])
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results
            )
            
            docs = results['documents'][0] if results.get('documents') else []
            metas = results['metadatas'][0] if results.get('metadatas') else []
            return docs, metas
        except Exception as e:
            print(f"Error in dense search: {e}")
            return [], []

    def search_bm25(self, query, n_results=3):
        """Sparse lexical search using BM25"""
        if not self.bm25 or not self.documents:
            return [], []

        tokenized_query = self._tokenize(query)
        if not tokenized_query:
            return [], []

        doc_scores = self.bm25.get_scores(tokenized_query)
        # Pair with indices and sort by score descending
        scored_docs = sorted(
            enumerate(doc_scores),
            key=lambda x: x[1],
            reverse=True
        )

        top_indices = [idx for idx, score in scored_docs[:n_results] if score > 0]
        results_docs = [self.documents[i] for i in top_indices]
        results_meta = [self.metadatas[i] for i in top_indices]
        return results_docs, results_meta

    def hybrid_search(self, query, n_results=3, rrf_k=60):
        """
        Hybrid Search combining BM25 (Keywords) + ChromaDB (Semantic HNSW)
        using Reciprocal Rank Fusion (RRF).
        """
        if not self.documents and self.collection.count() == 0:
            return [], []

        candidate_k = max(n_results * 2, 5)
        
        # 1. Fetch dense vector results
        dense_docs, dense_metas = self.search_dense(query, n_results=candidate_k)
        
        # 2. Fetch BM25 lexical results
        bm25_docs, bm25_metas = self.search_bm25(query, n_results=candidate_k)

        # 3. Reciprocal Rank Fusion (RRF) scoring
        rrf_scores = {}  # doc_text -> score
        doc_metadata_map = {}
        match_types = {}  # doc_text -> 'hybrid' | 'semantic' | 'keyword'

        # Score Dense Ranks
        for rank, (doc, meta) in enumerate(zip(dense_docs, dense_metas)):
            rrf_scores[doc] = rrf_scores.get(doc, 0.0) + (1.0 / (rrf_k + rank + 1))
            doc_metadata_map[doc] = meta
            match_types[doc] = "semantic"

        # Score BM25 Ranks
        for rank, (doc, meta) in enumerate(zip(bm25_docs, bm25_metas)):
            if doc in rrf_scores:
                match_types[doc] = "hybrid (keyword + semantic)"
            else:
                match_types[doc] = "keyword (BM25)"
            rrf_scores[doc] = rrf_scores.get(doc, 0.0) + (1.0 / (rrf_k + rank + 1))
            doc_metadata_map[doc] = meta

        # 4. Sort documents by combined RRF score
        sorted_docs = sorted(rrf_scores.keys(), key=lambda d: rrf_scores[d], reverse=True)
        top_docs = sorted_docs[:n_results]
        
        top_metas = []
        for d in top_docs:
            meta = dict(doc_metadata_map.get(d, {}))
            meta["match_type"] = match_types.get(d, "unknown")
            meta["rrf_score"] = round(rrf_scores.get(d, 0.0), 4)
            top_metas.append(meta)

        return top_docs, top_metas

    def search(self, query, n_results=3):
        """Default search method defaults to Hybrid Search"""
        return self.hybrid_search(query, n_results=n_results)
