import requests
import json

url = "http://localhost:11434/api/chat"
model = "srilanka-llama"

payload = {
    "model": model,
    "messages": [
        {"role": "user", "content": "Hello, are you ready to plan a trip to Sri Lanka?"}
    ],
    "stream": False
}

print(f"Testing connection to {model} at {url}...")

try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ SUCCESS! Ollama is running.")
        print("Response:", response.json()['message']['content'])
    else:
        print(f"❌ Failed: HTTP {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Connection Error: {e}")
