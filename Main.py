import tkinter as tk
from tkinter import scrolledtext
import google.generativeai as genai
import re
import json
from datetime import datetime
from prompt import prompt_multilingual

# Gemini API Key
genai.configure(api_key="AIzaSyCJ36BPXn3J2wDaNnY9nG8OetE3NUOzYcM")  # Replace with your key

# --- GUI Setup ---
window = tk.Tk()
window.title("🍕 DESKTECH Pizza Assistant")
window.geometry("720x620")
window.configure(bg="#fff4e6")

# --- Language Selection ---
language_var = tk.StringVar(window)
language_var.set("en")  # Default to English

languages = {
    "English": "en",
    "Arabic": "ar",
    "German": "de",
    "Russian": "ru"
}

def set_language_and_initialize():
    global chat
    lang_code = language_var.get()
    selected_prompt = prompt_multilingual.get(lang_code, prompt_multilingual["en"])
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=selected_prompt
    )
    chat = model.start_chat(history=[])
    try:
        response = chat.send_message("Hello")
        initial_text = response.text
    except Exception as e:
        initial_text = f"⚠️ Failed to initialize assistant: {e}"
    chat_display.config(state='normal')
    chat_display.delete("1.0", tk.END)
    chat_display.config(state='disabled')
    append_message("DESKTECH", initial_text)

lang_frame = tk.Frame(window, bg="#fff4e6")
tk.Label(lang_frame, text="Select Language:", bg="#fff4e6", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(10, 5))
lang_menu = tk.OptionMenu(lang_frame, language_var, *languages.values())
lang_menu.pack(side=tk.LEFT)
lang_button = tk.Button(lang_frame, text="Start", command=set_language_and_initialize, bg="#d35400", fg="white")
lang_button.pack(side=tk.LEFT, padx=10)
lang_frame.pack(pady=(10, 0))

# --- Chat Display ---
chat_display = scrolledtext.ScrolledText(window, wrap=tk.WORD, state='disabled', font=("Segoe UI", 11), bg="#fffaf0")
chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

user_input = tk.Entry(window, font=("Segoe UI", 12), bg="#fff", fg="#333")
user_input.pack(fill=tk.X, padx=10, pady=(0, 5))

# --- Utility Functions ---
def clean_response(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text

def append_message(sender, message):
    message = clean_response(message)
    chat_display.config(state='normal')
    if sender == "You":
        chat_display.insert(tk.END, f"{sender}: {message}\n\n", 'user')
    elif sender == "DESKTECH":
        chat_display.insert(tk.END, f"{sender}: {message}\n\n", 'assistant')
    else:
        chat_display.insert(tk.END, f"{sender}: {message}\n\n", 'error')
    chat_display.config(state='disabled')
    chat_display.yview(tk.END)

chat_display.tag_config('user', foreground='#006400')
chat_display.tag_config('assistant', foreground='#8B0000')
chat_display.tag_config('error', foreground='#ff0000')

def save_order_to_json(order):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"order_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(order, f, indent=4, ensure_ascii=False)
        append_message("System", f"✅ Order saved to {filename}")
    except Exception as e:
        append_message("Error", f"⚠️ Failed to save order: {e}")

# --- Send Message Logic ---
def send_message():
    message = user_input.get().strip()
    if not message or not chat:
        return
    append_message("You", message)
    user_input.delete(0, tk.END)

    try:
        response = chat.send_message(message)
        response_text = response.text
        append_message("DESKTECH", response_text)

        if "final order" in response_text.lower() or "order summary" in response_text.lower():
            structured_order = {}

            name_match = re.search(r"name[:\-]?\s*([\w\s]+)", response_text, re.IGNORECASE)
            if name_match:
                structured_order["customer_name"] = name_match.group(1).strip()

            phone_match = re.search(r"phone[:\-]?\s*([\d +]+)", response_text, re.IGNORECASE)
            if phone_match:
                structured_order["phone"] = phone_match.group(1).strip()

            address_match = re.search(r"address[:\-]?\s*(.+)", response_text, re.IGNORECASE)
            if address_match:
                structured_order["delivery_address"] = address_match.group(1).strip()

            pizza_types = re.findall(r"(Margherita|Pepperoni|Veggie Delight|Chicken Supreme|BBQ Beef|Seafood Special|Spicy Lamb|Four Cheese)", response_text, re.IGNORECASE)
            sizes = re.findall(r"\b(Small|Medium|Large)\b", response_text, re.IGNORECASE)
            crusts = re.findall(r"(Thin|Thick|Stuffed|Gluten-Free) Crust", response_text, re.IGNORECASE)
            toppings = re.findall(r"(Mushrooms|Onions|Olives|Extra Cheese|Pineapple|Jalapeños|Spinach|Tuna|Egg)", response_text, re.IGNORECASE)

            pizzas = []
            pizza_count = max(len(pizza_types), len(sizes), len(crusts))
            for i in range(pizza_count):
                pizza = {
                    "type": pizza_types[i].title() if i < len(pizza_types) else "Unknown",
                    "size": sizes[i].title() if i < len(sizes) else "Unknown",
                    "crust": crusts[i].title() + " Crust" if i < len(crusts) else "Unknown",
                    "toppings": list(set([t.title() for t in toppings])) if toppings else []
                }
                pizzas.append(pizza)

            structured_order["pizzas"] = pizzas
            structured_order["halal"] = "halal" in response_text.lower()

            allergies_match = re.search(r"allerg(?:y|ies)[:\-]?\s*(.+?)(?:\.|\n|$)", response_text, re.IGNORECASE)
            structured_order["allergies"] = allergies_match.group(1).strip() if allergies_match else "None"

            payment_method = None
            if "paypal" in response_text.lower():
                payment_method = "PayPal"
            elif "bank transfer" in response_text.lower():
                payment_method = "Bank Transfer"
            elif "card" in response_text.lower():
                payment_method = "Card"
            elif "cash" in response_text.lower():
                payment_method = "Cash"
            if payment_method:
                structured_order["payment"] = {"method": payment_method}

            total_match = re.search(r"Total[:\s]*(€|EUR)?\s?(\d+[\.,]?\d*)", response_text, re.IGNORECASE)
            if total_match:
                total = float(total_match.group(2).replace(",", "."))
                structured_order.setdefault("payment", {})["total"] = round(total, 2)
            else:
                # fallback: sum all prices found
                price_matches = re.findall(r"(€|EUR)\s?(\d+[\.,]?\d*)", response_text)
                if price_matches:
                    total = 0.0
                    for _, price_str in price_matches:
                        total += float(price_str.replace(",", "."))
                    structured_order.setdefault("payment", {})["total"] = round(total, 2)

            save_order_to_json(structured_order)

    except Exception as e:
        append_message("Error", f"⚠️ {str(e)}")

# --- Send Button ---
send_button = tk.Button(window, text="Send", command=send_message, font=("Segoe UI", 11), bg="#d35400", fg="white")
send_button.pack(pady=(0, 10))
window.bind('<Return>', lambda event: send_message())

# --- Init chat with placeholder ---
chat = None

# --- Start GUI ---
window.mainloop()
