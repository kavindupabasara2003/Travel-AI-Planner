import sys
import os
import requests
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from travel_api.services.llama_service import LLaMAService

def get_cosine_sim(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def test_similarity():
    llama = LLaMAService()
    
    # Text parsed the old way from dict
    old_text1 = "7 days trip to Sri Lanka starting from Colombo for a Couple. Style: Beach."
    old_text2 = "7 days trip to Sri Lanka starting from Kandy for a Couple. Style: Adventure."
    
    # Text parsed the new way from dict
    new_text1 = "Duration: 7 Days | Start Location: Colombo | Group: Couple | Style: Beach"
    new_text2 = "Duration: 7 Days | Start Location: Kandy | Group: Couple | Style: Adventure"
    
    sim_old = get_cosine_sim(llama.get_embedding(old_text1), llama.get_embedding(old_text2))
    sim_new = get_cosine_sim(llama.get_embedding(new_text1), llama.get_embedding(new_text2))
    
    print(f"OLD METHOD Similarity: {sim_old:.4f}")
    print(f"NEW METHOD Similarity: {sim_new:.4f}")

if __name__ == "__main__":
    test_similarity()
