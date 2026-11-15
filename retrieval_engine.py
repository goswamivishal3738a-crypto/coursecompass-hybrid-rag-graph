import pandas as pd
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import faiss

class HybridRetriever:
    def __init__(self, csv_path):
        print("Loading processed data...")
        self.df = pd.read_csv(csv_path)
        self.passages = self.df['text_passage'].tolist()
        self.sources = self.df['source_document'].tolist()
        
        print("1. Building BM25 Keyword Index...")
        # Simple tokenization for BM25
        self.tokenized_passages = [str(doc).lower().split() for doc in self.passages]
        self.bm25 = BM25Okapi(self.tokenized_passages)
        
        print("2. Building FAISS Semantic Index...")
        
        # all-MiniLM-L6-v2 is a fast and lightweight model for sentence embeddings
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2') 
        self.embeddings = self.embedder.encode(self.passages, convert_to_numpy=True)
        
        # Initialize FAISS Index (L2 distance)
        dimension = self.embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index.add(self.embeddings)
        print("=> Initialization Complete!\n")

    def bm25_search(self, query, top_k=5):
        """Traditional Keyword Search"""
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for rank, idx in enumerate(top_indices):
            results.append({
                'doc_id': idx,
                'source': self.sources[idx],
                'text': self.passages[idx],
                'score': scores[idx],
                'rank': rank + 1
            })
        return results

    def semantic_search(self, query, top_k=5):
        """Semantic Vector Search using FAISS"""
        query_embedding = self.embedder.encode([query], convert_to_numpy=True)
        distances, indices = self.faiss_index.search(query_embedding, top_k)
        
        results = []
        for rank, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            results.append({
                'doc_id': idx,
                'source': self.sources[idx],
                'text': self.passages[idx],
                'score': 1 / (1 + dist),  # Convert distance to a similarity score
                'rank': rank + 1
            })
        return results

    def hybrid_rrf_search(self, query, top_k=3, rrf_k=60):
        """Combines BM25 and Semantic Search using Reciprocal Rank Fusion (RRF)"""
        bm25_results = self.bm25_search(query, top_k=10) # Fetch top 10 for fusion
        semantic_results = self.semantic_search(query, top_k=10)
        
        rrf_scores = {}
        
        # Add RRF scores from BM25
        for res in bm25_results:
            doc_id = res['doc_id']
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (rrf_k + res['rank']))
            
        # Add RRF scores from Semantic Search
        for res in semantic_results:
            doc_id = res['doc_id']
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (rrf_k + res['rank']))
            
        # Sort documents by their combined RRF score
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        final_results = []
        for doc_id, score in sorted_docs:
            final_results.append({
                'source': self.sources[doc_id],
                'text': self.passages[doc_id],
                'rrf_score': score
            })
        return final_results

# Testing the Engine 
if __name__ == "__main__":
    retriever = HybridRetriever("data/processed_corpus.csv")
    
    # Using one of the proposed test queries from your synopsis
    test_query = "What prerequisites are required to understand deep learning?"
    print(f"--- Testing Query: '{test_query}' ---\n")
    
    print("=== Hybrid RRF Results ===")
    for idx, res in enumerate(retriever.hybrid_rrf_search(test_query, top_k=2)):
        print(f"Result [{idx+1}] (Score: {res['rrf_score']:.4f})")
        print(f"Content: {res['text']}\n")