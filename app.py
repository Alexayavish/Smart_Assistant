from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import re
import os
import json
from prompts import SYSTEM_PROMPT_EN, SYSTEM_PROMPT_AR, SYSTEM_PROMPT_RU, SYSTEM_PROMPT_DE
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

SYSTEM_PROMPTS = {
    "en": SYSTEM_PROMPT_EN,
    "ar": SYSTEM_PROMPT_AR,
    "ru": SYSTEM_PROMPT_RU,
    "de": SYSTEM_PROMPT_DE,
}

ORDER_FILE = "orders.json"

def clean_response(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text

def get_user_id():
    return request.remote_addr  # Simplified per-user tracking

def save_order(user_id, order_data, chat_history):
    try:
        if os.path.exists(ORDER_FILE):
            with open(ORDER_FILE, "r", encoding="utf-8") as f:
                all_orders = json.load(f)
        else:
            all_orders = {}

        all_orders[user_id] = {
            "order_data": order_data,
            "chat_history": chat_history
        }

        with open(ORDER_FILE, "w", encoding="utf-8") as f:
            json.dump(all_orders, f, indent=2)
    except Exception as e:
        print(f"Error saving order: {e}")

def load_user_data(user_id):
    try:
        if os.path.exists(ORDER_FILE):
            with open(ORDER_FILE, "r", encoding="utf-8") as f:
                all_orders = json.load(f)
                return all_orders.get(user_id)
    except Exception as e:
        print(f"Error loading user data: {e}")
    return None

def extract_order_from_reply(reply_text):
    try:
        match = re.search(r"(?<=```json)(.*?)(?=```)", reply_text, re.DOTALL)
        if match:
            json_str = match.group(0).strip()
            return json.loads(json_str)
        return None
    except Exception as e:
        print(f"Error extracting order: {e}")
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    user_message = request.json.get("message", "").strip()
    language = request.json.get("language", "en").lower()
    if language not in SYSTEM_PROMPTS:
        language = "en"

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    try:
        user_id = get_user_id()
        user_data = load_user_data(user_id)
        previous_order = user_data.get("order_data") if user_data else None
        previous_history = user_data.get("chat_history") if user_data else []

        # Build system prompt only if this is the first message
        if not previous_history:
            system_prompt = SYSTEM_PROMPTS[language]
            if previous_order:
                system_prompt += f"\n\nHere is the user's current order:\n{json.dumps(previous_order, indent=2)}"
            previous_history = [{"role": "user", "parts": [system_prompt]}]

        chat = model.start_chat(history=previous_history)
        response = chat.send_message(user_message)
        reply = clean_response(response.text)

        # Update order if new info is found
        order_data = extract_order_from_reply(response.text)
        if not order_data and previous_order:
            order_data = previous_order

        # Save chat and order
        save_order(user_id, order_data, chat.history)

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Reset orders.json on server start
with open("orders.json", "w", encoding="utf-8") as f:
    json.dump({}, f)

if __name__ == "__main__":
    app.run(debug=True)
