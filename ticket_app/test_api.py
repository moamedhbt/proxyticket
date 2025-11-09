import requests

API_KEY = "AIzaSyCN2p6WIpPzqeRsmRjeEsi324dvBmDZmnI"
MODEL = "gemini-2.5-flash"

url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent?key={API_KEY}"

headers = {
    "Content-Type": "application/json"
}

body = {
    "contents": [{
        "role": "user",
        "parts": [{
            "text": "Translate 'hello' to French"
        }]
    }]
}

try:
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    print("API Test Successful!")
    print("Response:", response.json())
except Exception as e:
    print("API Test Failed!")
    print("Error:", str(e))
