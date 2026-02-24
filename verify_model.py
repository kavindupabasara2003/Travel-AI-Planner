import requests
import json

def test_model():
    url = "http://localhost:11434/api/generate"
    prompt = "Where is Lords Restaurant located?"
    
    payload = {
        "model": "srilanka-llama",
        "prompt": prompt,
        "stream": False
    }
    
    print(f"Testing Model: {payload['model']}")
    print(f"Prompt: {prompt}")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        print("\nResponse:")
        print(result['response'])
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_model()
