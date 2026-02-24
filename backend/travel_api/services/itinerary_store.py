import os
import json
import numpy as np
from pathlib import Path

class ItineraryStore:
    def __init__(self, data_dir=None):
        if data_dir is None:
            # Default to a folder in the project root
            self.base_dir = Path(__file__).parent.parent.parent / "data" / "cache"
        else:
            self.base_dir = Path(data_dir)
            
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.base_dir / "itinerary_index.json"
        self.vectors_file = self.base_dir / "itinerary_vectors.npy"
        
        self.itineraries = self._load_index()
        self.vectors = self._load_vectors()

    def _load_index(self):
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                return json.load(f)
        return []

    def _load_vectors(self):
        if self.vectors_file.exists():
            return np.load(self.vectors_file)
        return np.empty((0, 0))

    def save(self, query, embedding, itinerary_data):
        """Save a new itinerary and its embedding."""
        # Add to index
        self.itineraries.append({
            "query": query,
            "data": itinerary_data
        })
        
        # Update vectors
        new_vec = np.array(embedding).reshape(1, -1)
        if self.vectors.size == 0:
            self.vectors = new_vec
        else:
            # Ensure dimensions match
            if new_vec.shape[1] != self.vectors.shape[1]:
                print(f"Warning: Vector dimension mismatch. Expected {self.vectors.shape[1]}, got {new_vec.shape[1]}")
                return
            self.vectors = np.vstack([self.vectors, new_vec])
            
        # Write to disk
        with open(self.index_file, "w") as f:
            json.dump(self.itineraries, f)
        np.save(self.vectors_file, self.vectors)

    def find_similar(self, query_text, query_embedding, threshold=0.995):
        """Find an itinerary with high cosine similarity."""
        if self.vectors.size == 0:
            return None
            
        # Fast path exact match (bypassing broken embedding models that score 1.0)
        for itinerary in self.itineraries:
            if itinerary.get("query") == query_text:
                print(f"✅ Exact String Match Cache Hit!")
                return itinerary["data"]

        # Normalize vectors for cosine similarity
        norm_vectors = self.vectors / np.linalg.norm(self.vectors, axis=1, keepdims=True)
        norm_query = np.array(query_embedding) / np.linalg.norm(query_embedding)
        
        # Calculate similarities
        similarities = np.dot(norm_vectors, norm_query)
        
        # Find best match
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        print(f"DEBUG: Best cache match score: {best_score:.4f}")
        
        if best_score >= threshold:
            # CRITICAL FIX: nomic-embed-text often gives 1.0 scores to different strings.
            # We must enforce that the actual query strings are also highly similar or identical 
            # to prevent a "Beach" trip from serving as an "Adventure" trip.
            cached_query = self.itineraries[best_idx].get("query", "")
            if cached_query == query_text:
                print(f"✅ Cache Hit! Strict String Match Verified. (Score: {best_score:.4f})")
                return self.itineraries[best_idx]["data"]
            else:
                print(f"❌ False Positive Vector Hit! Score: {best_score:.4f}, but text '{query_text}' != '{cached_query}'. Rejecting.")
                return None
            
        return None
