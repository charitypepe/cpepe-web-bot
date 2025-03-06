from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from langdetect import detect
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

# Информация от сайта
CPEPE_INFO = """
$CPEPE е DeFi екосистема, стартираща на 7 март 2025 г. с общ запас от 1 трилион токена.
За да купите $CPEPE:
1. Посетете https://charitypepe.com
2. Свържете MetaMask или друг Ethereum портфейл
3. Участвайте в пресейла: Pre-sale 1 - $0.0001, Pre-sale 2 - $0.0002
4. Очаквайте до 20x-22x възвръщаемост след листинг!
"""

# Поддържани езици
SUPPORTED_LANGUAGES = ["en", "bg", "de", "es", "fr", "ru", "it"]

# Функция за разпознаване на език
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

# Инициализирай клиента
client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.route("/send_to_bot", methods=["POST"])
def send_to_bot():
    data = request.json
    message = data.get("message")
    source = data.get("source", "website")

    if not message:
        return jsonify({"response": "Error: No message provided"})
    
    lang = detect_language(message)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an AI assistant for CharityPEPE ($CPEPE), an ERC-20 token on Ethereum. Answer in the language of the message (detected as '{lang}'). Use this info:\n\n{CPEPE_INFO}"},
                {"role": "user", "content": message}
            ]
        )
        bot_response = response.choices[0].message.content
        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)