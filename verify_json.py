import requests
import json

def test_json_generation():
    url = "http://localhost:11434/api/generate"
    # Prompt explicitly asking for JSON as per the Modelfile system prompt
    prompt = "Plan a 2 day trip to Kandy for a couple interested in culture. Output JSON."
    
    payload = {
        "model": "srilanka-llama",
        "prompt": prompt,
        "stream": False,
        "format": "json" # Force JSON mode in Ollama
    }
    
    print(f"Testing JSON Generation: {payload['model']}")
    print(f"Prompt: {prompt}")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        print("\nResponse:")
        print(result['response'])
        
        # Validate JSON
        try:
            parsed = json.loads(result['response'])
            print("\n✅ Valid JSON detected!")
            print(f"Keys: {list(parsed.keys())}")
        except json.JSONDecodeError:
            print("\n❌ Invalid JSON")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_json_generation()
