import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# === CONFIGURATION ===
API_KEY = "AIzaSyCN2p6WIpPzqeRsmRjeEsi324dvBmDZmnI"
MODEL = "gemini-1.5-flash"  # Using the working model from our test

app = Flask(__name__)
CORS(app)

@app.post("/translate")
def translate():
    data = request.get_json(silent=True) or {}
    items = data.get("list", [])
    if not isinstance(items, list):
        return jsonify({"ok": False, "error": "'list' must be an array"}), 400

    # Prepare the prompt for translation
    prompt = (
        "Translate these French terms to Modern Standard Arabic. "
        "Return ONLY a JSON array of strings, same order.\n"
        + __import__("json").dumps(items, ensure_ascii=False)
    )

    # Prepare the request body matching the working test script
    body = {
        "contents": [{
            "role": "user",
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.8,
            "topK": 40
        }
    }

    url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent?key={API_KEY}"
    try:
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, headers=headers, json=body, timeout=30)
        r.raise_for_status()
        response_data = r.json()
        
        # Debug: Print the full response
        print("API Response:", response_data)
        
        # Extract the translated text from the response
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            parts = response_data['candidates'][0].get('content', {}).get('parts', [])
            if parts and 'text' in parts[0]:
                translated_text = parts[0]['text'].strip()
                # Try to parse the response as JSON
                try:
                    arr = __import__("json").loads(translated_text)
                    if isinstance(arr, list):
                        return jsonify(arr)
                except json.JSONDecodeError:
                    # If not valid JSON, try to extract array from markdown code blocks
                    import re
                    json_match = re.search(r'```(?:json)?\n(\[.*?\])\n```', translated_text, re.DOTALL)
                    if json_match:
                        try:
                            arr = __import__("json").loads(json_match.group(1))
                            if isinstance(arr, list):
                                return jsonify(arr)
                        except:
                            pass
                    
                    # If all else fails, return the raw text
                    return jsonify([translated_text])
        
        # If we get here, something went wrong with the response format
        return jsonify({"error": "Unexpected API response format", "response": response_data}), 502
    except requests.HTTPError as e:
        return jsonify({"ok": False, "error": f"HTTP {e.response.status_code}", "raw": e.response.text}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Proxy running at http://localhost:3000/translate")
    app.run(host="0.0.0.0", port=3000)
