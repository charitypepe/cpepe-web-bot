from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from langdetect import detect
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Грешка: Липсва OpenAI API ключ! Задайте го в .env или в средата.")

# Инициализирай клиента без допълнителни аргументи
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Останалата част от кода остава до send_to_bot()
@app.route("/send_to_bot", methods=["POST"])
def send_to_bot():
    data = request.json
    message = data.get("message")
    source = data.get("source", "website")

    if not message:
        return jsonify({"response": "Error: No message provided"})
    
    lang = detect_language(message)

    try:
        # Нов синтаксис за чат заявка
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