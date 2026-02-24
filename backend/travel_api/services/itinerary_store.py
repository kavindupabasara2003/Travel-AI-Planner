import json
from travel_api.models import ItineraryCache
from pgvector.django import CosineDistance

class ItineraryStore:
    def __init__(self, data_dir=None):
        pass # Data dir is obsolete, we use PostgreSQL natively now

    def save(self, query, embedding, itinerary_data):
        """Save a new itinerary and its pgvector embedding to PostgreSQL."""
        # Optional: check if exact query already exists to avoid duplicate logic
        if not ItineraryCache.objects.filter(query_text=query).exists():
            ItineraryCache.objects.create(
                query_text=query,
                embedding=embedding,
                itinerary_json=itinerary_data
            )
            print("💾 Saved new vector embedding to PostgreSQL ItineraryCache.")

    def find_similar(self, query_text, query_embedding, threshold=0.995):
        """Find an itinerary with high cosine similarity natively via pgvector."""
        
        # Fast path exact match (bypassing expensive vector ops)
        exact_match = ItineraryCache.objects.filter(query_text=query_text).first()
        if exact_match:
            print(f"✅ Exact String Match Cache Hit! (PostgreSQL)")
            return exact_match.itinerary_json

        # In pgvector, CosineDistance represents (1 - cosine_similarity).
        # Therefore, to check for similarity >= 0.995, we check distance <= 0.005
        max_distance = 1.0 - threshold
        
        # Native pgvector cosine distance calculation in the database
        match = ItineraryCache.objects.annotate(
            distance=CosineDistance('embedding', query_embedding)
        ).order_by('distance').first()
        
        if match:
            print(f"DEBUG: Best cache match distance: {match.distance:.4f} (Required <= {max_distance:.4f})")
            
            if match.distance <= max_distance:
                # We reached the vector threshold, but strictly verify string equivalence mapping
                if match.query_text == query_text:
                    print(f"✅ Cache Hit! Vector Match Verified. (Distance: {match.distance:.4f})")
                    return match.itinerary_json
                else:
                    print(f"❌ False Positive Vector Hit! Distance: {match.distance:.4f}, but text '{query_text}' != '{match.query_text}'. Rejecting.")
                    return None
            
        return None
