from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from langdetect import detect
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import threading
import time

app = Flask(__name__)
CORS(app)

# Линкове към разделите на сайта
SITE_URLS = [
    "https://www.charitypepe.com/",
    "https://charitypepe.github.io/charitypepe-presale/",
    "https://www.charitypepe.com/tokenomics",
    "https://www.charitypepe.com/whitepaper",
    "https://www.charitypepe.com/kontakt"
]

# Глобална променлива за информацията
SITE_INFO = "Информацията се актуализира..."

def update_site_info():
    global SITE_INFO
    while True:
        combined_info = ""
        for url in SITE_URLS:
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                page_text = soup.get_text(separator=" ").strip()
                combined_info += f"\n\nИнформация от {url}:\n{page_text[:500]}"  # Ограничаваме на 500 символа на страница
            except Exception as e:
                combined_info += f"\n\nГрешка при четене на {url}: {e}"
        SITE_INFO = combined_info.strip()
        print("Информацията от сайта е актуализирана!")
        time.sleep(600)  # 10 минути

SUPPORTED_LANGUAGES = ["en", "bg", "de", "es", "fr", "ru", "it"]

def detect_language(message):
    try:
        lang = detect(message)
        return lang if lang in SUPPORTED_LANGUAGES else "en"
    except Exception as e:
        print(f"Error detecting language: {e}")
        return "en"

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Грешка: Липсва OpenAI API ключ! Задайте го в .env или в средата.")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.route("/send_to_bot", methods=["POST"])
def send_to_bot():
    data = request.json
    message = data.get("message")
    source = data.get("source", "website")

    if not message:
        return jsonify({"response": "Error: No message provided"})
    
    lang = detect_language(message)
    full_message = f"{message}\n\nАктуална информация от сайта:\n{SITE_INFO}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an AI assistant for CharityPEPE ($CPEPE), an ERC-20 token on Ethereum. Answer in the language of the message (detected as '{lang}'). Use the provided site info to give detailed, up-to-date answers:\n\n{full_message}"},
                {"role": "user", "content": message}
            ]
        )
        bot_response = response.choices[0].message.content
        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

if __name__ == "__main__":
    threading.Thread(target=update_site_info, daemon=True).start()
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)