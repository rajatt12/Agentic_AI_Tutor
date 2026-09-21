import os
import re
import glob
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

class EmbeddingManager:
    def __init__(self, collection_name="study_materials", db_path="./database/vector_store"):
        """Initialize EmbeddingManager with ChromaDB (HNSW) and BM25 Lexical Index with student isolation"""
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

        # Automatically seed core curriculum files if knowledge base is fresh
        self.seed_curriculum_if_needed()

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

    def seed_curriculum_if_needed(self, curriculum_dir="./data/curriculum"):
        """Pre-seed standard shared curriculum sheets (Physics, Math, Chemistry)"""
        try:
            # Check if curriculum is already seeded
            stored = self.collection.get(where={"student_id": "global_curriculum"})
            if stored and stored.get('documents') and len(stored['documents']) > 0:
                return

            if not os.path.exists(curriculum_dir):
                return

            txt_files = glob.glob(os.path.join(curriculum_dir, "*.txt"))
            for file_path in txt_files:
                basename = os.path.basename(file_path)
                subject = basename.split("_")[0].capitalize()
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Split by sections ## or double newlines
                sections = [s.strip() for s in content.split("## ") if s.strip()]
                chunks = []
                metas = []
                for sec in sections:
                    lines = sec.split("\n", 1)
                    title = lines[0].strip() if len(lines) > 1 else f"{subject} Section"
                    body = lines[1].strip() if len(lines) > 1 else sec
                    
                    # Further chunk if long
                    sub_chunks = [c.strip() for c in body.split("\n\n") if len(c.strip()) > 30]
                    if not sub_chunks:
                        sub_chunks = [body]
                    
                    for sc in sub_chunks:
                        chunks.append(f"[{subject} - {title}]\n{sc}")
                        metas.append({
                            "student_id": "global_curriculum",
                            "is_shared": True,
                            "title": f"{subject}: {title}",
                            "subject": subject,
                            "source": "curriculum_library"
                        })

                if chunks:
                    self.add_documents(chunks, metas)
        except Exception as e:
            print(f"Warning: Curriculum seeding error: {e}")

    def add_documents(self, documents, metadata=None):
        """Add study materials to both ChromaDB (Dense) and BM25 (Sparse) indexes"""
        if not documents:
            return
        
        if metadata is None:
            metadata = [{"is_shared": True, "student_id": "global_curriculum"} for _ in documents]

        # Ensure every metadata dictionary has is_shared and student_id
        for m in metadata:
            if "is_shared" not in m:
                m["is_shared"] = False
            if "student_id" not in m:
                m["student_id"] = "global_curriculum" if m.get("is_shared") else "default_student"

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

    def search_dense(self, query, student_id=None, n_results=3):
        """Dense semantic search using ChromaDB with dual-tier scope filtering (Public + Student Private)"""
        try:
            count = self.collection.count()
            if count == 0:
                return [], []
            
            n_results = min(n_results, count)
            query_embedding = self.model.encode([query])
            
            # Dual-Tier Filter: (is_shared == True) OR (student_id == current_student)
            where_filter = None
            if student_id and student_id != "global_curriculum":
                where_filter = {
                    "$or": [
                        {"is_shared": {"$eq": True}},
                        {"student_id": {"$eq": student_id}}
                    ]
                }
            elif student_id == "global_curriculum":
                where_filter = {"is_shared": {"$eq": True}}

            query_kwargs = {
                "query_embeddings": query_embedding.tolist(),
                "n_results": n_results
            }
            if where_filter:
                query_kwargs["where"] = where_filter

            results = self.collection.query(**query_kwargs)
            
            docs = results['documents'][0] if results.get('documents') else []
            metas = results['metadatas'][0] if results.get('metadatas') else []
            return docs, metas
        except Exception as e:
            # Fallback if where filter on $or has single element or syntax nuance
            try:
                query_kwargs.pop("where", None)
                results = self.collection.query(**query_kwargs)
                docs = results['documents'][0] if results.get('documents') else []
                metas = results['metadatas'][0] if results.get('metadatas') else []
                return docs, metas
            except Exception:
                return [], []

    def search_bm25(self, query, student_id=None, n_results=3):
        """Sparse lexical search using BM25 scoped to Public Library + Student Private Notes"""
        if not self.bm25 or not self.documents:
            return [], []

        tokenized_query = self._tokenize(query)
        if not tokenized_query:
            return [], []

        doc_scores = self.bm25.get_scores(tokenized_query)
        
        # Filter matching candidates accessible to this student
        scored_docs = []
        for idx, score in enumerate(doc_scores):
            if score <= 0:
                continue
            meta = self.metadatas[idx] if idx < len(self.metadatas) else {}
            is_shared = meta.get("is_shared", True)
            doc_student = meta.get("student_id", "global_curriculum")
            
            # Accessible if shared OR owned by this student
            if is_shared or (student_id and doc_student == student_id):
                scored_docs.append((idx, score))

        scored_docs.sort(key=lambda x: x[1], reverse=True)

        top_indices = [idx for idx, _ in scored_docs[:n_results]]
        results_docs = [self.documents[i] for i in top_indices]
        results_meta = [self.metadatas[i] for i in top_indices]
        return results_docs, results_meta

    def hybrid_search(self, query, student_id=None, n_results=3, rrf_k=60):
        """
        Hybrid Search combining BM25 (Keywords) + ChromaDB (Semantic HNSW)
        using Reciprocal Rank Fusion (RRF) scoped to Public Library + Student Notes.
        """
        if not self.documents and self.collection.count() == 0:
            return [], []

        candidate_k = max(n_results * 2, 5)
        
        # 1. Fetch dense vector results
        dense_docs, dense_metas = self.search_dense(query, student_id=student_id, n_results=candidate_k)
        
        # 2. Fetch BM25 lexical results
        bm25_docs, bm25_metas = self.search_bm25(query, student_id=student_id, n_results=candidate_k)

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

    def search(self, query, student_id=None, n_results=3):
        """Default search method defaults to Hybrid Search"""
        return self.hybrid_search(query, student_id=student_id, n_results=n_results)

    def get_student_documents(self, student_id: str):
        """List personal documents for a student + shared curriculum overview"""
        student_docs = []
        shared_count = 0
        seen_titles = set()

        for doc, meta in zip(self.documents, self.metadatas):
            is_shared = meta.get("is_shared", False)
            doc_student = meta.get("student_id", "")
            title = meta.get("title", "Untitled Note")

            if is_shared:
                shared_count += 1
            elif doc_student == student_id:
                if title not in seen_titles:
                    seen_titles.add(title)
                    student_docs.append({
                        "title": title,
                        "subject": meta.get("subject", "General"),
                        "preview": doc[:120] + "..." if len(doc) > 120 else doc,
                        "is_shared": False
                    })

        return {
            "student_id": student_id,
            "personal_notes": student_docs,
            "shared_curriculum_chunks": shared_count
        }
