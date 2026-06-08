from flask import Flask, request, jsonify
from flask_cors import CORS
import os
#import google.generativeai as genai
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)

from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Configure Gemini API key
#genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the Gemini model
#model = genai.GenerativeModel("models/gemini-2.0-flash")

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json() or {}
    text = data.get("text")
    url = data.get("url")

    # If a URL is provided, fetch the page and extract text
    if url:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
        except Exception as e:
            return jsonify({"error": f"Failed to fetch URL: {str(e)}"}), 400

    if not text:
        return jsonify({"error": "No text or URL provided"}), 400

    prompt = f"""
You are a privacy assistant. Analyze the following privacy policy and do three things:
1. Summarize it in 3 simple bullet points.
2. Identify any concerning or invasive data practices.
3. Recommend whether the user should accept the policy or be cautious, and explain why in 1–2 sentences.
4. But make sure to keep it concise and talk in a very human way (max 100 words in total to do everything)

Here is the policy:
{text[:8000]}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return jsonify({"summary": completion.choices[0].message.content})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Optional health check route
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "Server is running."})

@app.route("/")
def home():
    return jsonify({"status": "Privacy API running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
