import requests

payload = {
    "model": "srilanka-llama",
    "messages": [
        {"role": "user", "content": "Hello, generate a tiny JSON."}
    ],
    "stream": False,
    "format": "json",
}

response = requests.post("http://127.0.0.1:11434/api/chat", json=payload)
print(response.json())
