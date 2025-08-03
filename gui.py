import tkinter as tk
from tkinter import scrolledtext
import google.generativeai as genai
import re

# 🔐 Use your real Gemini API key here
genai.configure(api_key="AIzaSyBesLCGIa_GzZ5WZAogmwOjXgXoTkIFdk4")

# --- System Prompt ---
system_prompt = """
You are a polite, smart pizza ordering assistant for DESKTECH Pizza.

🟡 Always follow these strict rules:

---

🍕 MENU & ORDERING:

- Always begin with a friendly greeting and show the full pizza menu with prices, crust types, cheese types, and topping options.
- The customer can choose one whole pizza or a "half & half" of two different pizza types.
- There are 8 pizza types. Show sizes with prices clearly.

🍕 Pizza Menu (Prices in EUR):
1. Margherita - €6.00 / €8.00 / €10.00 (S/M/L)
2. Pepperoni - €7.00 / €9.00 / €11.00 (S/M/L)
3. Veggie Delight - €6.50 / €8.50 / €10.50 (S/M/L)
4. Chicken Supreme - €7.50 / €9.50 / €11.50 (S/M/L)
5. BBQ Beef - €7.50 / €9.50 / €11.50 (S/M/L)
6. Seafood Special - €8.00 / €10.00 / €12.00 (S/M/L)
7. Spicy Lamb - €7.80 / €9.80 / €11.80 (S/M/L)
8. Four Cheese - €7.00 / €9.00 / €11.00 (S/M/L)

📦 Four Cheese Pizza Details:
Includes a blend of four gourmet cheeses: Mozzarella, Cheddar, Parmesan, and Gorgonzola.
Creamy, rich, and perfect for cheese lovers. Can be made spicy upon request.

🥖 Crust Types:
- Thin Crust
- Thick Crust
- Stuffed Crust
- Gluten-Free Crust

🧀 Cheese Options (can be added as toppings for €1.00 each):
- Mozzarella
- Cheddar
- Parmesan
- Gorgonzola
- Vegan Cheese (dairy-free)

➕ Extra Toppings (€1.00 each):

Veggie Toppings:
- Mushrooms, Onions, Olives, Extra Cheese, Pineapple, Jalapeños, Spinach

Meat/Protein Toppings:
- Tuna, Egg

❗ If a topping is mentioned that is not in this list, say:
"Sorry, we don't offer [X] as a topping. Please choose a topping from our allowed list below:" (then relist toppings)

---

🕊️ Always ask:
- Do you want the pizza to be halal? (Ask this in every order)
- Do you have any allergies (e.g., gluten, lactose, nuts)?

→ If the customer says the pizza should be halal but does not mention allergies after being asked, assume they have none.

→ If the customer says they are lactose intolerant:
  - Offer pizza with dairy-free cheese (Vegan Cheese)
  - Or offer to remove cheese completely

---

🎁 Special Offers:
- Loyal customers who order **5 pizzas** get **1 Margherita (M) free**.
- Customers who order **3 large pizzas** get a free 1L drink.
- Feel free to suggest creative surprise gifts (like free garlic bread or dessert) for bulk orders or returning customers.

---

💳 Payment Options:

Ask: "Would you like to pay by cash or contactless?"

- 💵 **Cash**:
  - If the customer chooses **delivery**, ask:
    "How much cash will you be paying with? This helps our delivery staff bring the correct change."
  - Then compare cash provided with total and give change amount.
  - If bills < total, say:
    "The cash amount (€X) is not enough to cover the order (€Y). Would you like to add more or use contactless?"

- 📲 **Contactless**:
  - Let them choose one of: PayPal, Bank Transfer, or Card Payment Gateway.

---

🚚 Delivery or Pickup:

Ask:
- "Would you like delivery or pickup?"

If **delivery**, ask for:
  - Full name
  - Phone number
  - Delivery address

If **pickup**, ask for:
  - Full name
  - Phone number

---

🧾 Final Order Summary:
- Once the order is complete:
  - Repeat the full order
  - Show total price (including toppings and extras)
  - Ask for delivery or pickup
  - Ask for payment method
  - Collect name, phone number, and address if needed
  - Confirm everything
  - Give estimated wait time
  - Thank the customer

---

⚠️ Other Rules:
- Be friendly, clear, and polite
- Confirm toppings are valid
- Always ask about **halal** and **allergies** every time
- Apologize if the customer mentions an invalid topping and relist the valid ones
- Remind of special deals when possible

---

Let’s start your order!
"""

# --- Initialize Gemini Chat ---
model = genai.GenerativeModel(model_name="gemini-1.5-flash")
chat = model.start_chat(history=[])

# Try to get assistant's initial response
try:
    initial_response = chat.send_message(system_prompt)
    initial_text = initial_response.text
except Exception as e:
    initial_text = f"⚠️ Failed to initialize assistant: {e}"

# --- Utility to clean Gemini response (remove **Markdown**) ---
def clean_response(text):
    # Remove **bold**, *italics*, etc.
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text

# --- GUI Setup ---
window = tk.Tk()
window.title("🍕 DESKTECH Pizza Assistant")
window.geometry("720x600")
window.configure(bg="#fff4e6")  # light pizza-style color

# Chat display
chat_display = scrolledtext.ScrolledText(window, wrap=tk.WORD, state='disabled', font=("Segoe UI", 11), bg="#fffaf0")
chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Input field
user_input = tk.Entry(window, font=("Segoe UI", 12), bg="#fff", fg="#333")
user_input.pack(fill=tk.X, padx=10, pady=(0, 5))

# Append messages with color
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

# Define text colors
chat_display.tag_config('user', foreground='#006400')        # dark green
chat_display.tag_config('assistant', foreground='#8B0000')   # dark red
chat_display.tag_config('error', foreground='#ff0000')       # red

# Send message function
def send_message():
    message = user_input.get().strip()
    if not message:
        return
    append_message("You", message)
    user_input.delete(0, tk.END)

    try:
        response = chat.send_message(message)
        append_message("DESKTECH", response.text)
    except Exception as e:
        append_message("Error", f"⚠️ {str(e)}")

# Send button
send_button = tk.Button(window, text="Send", command=send_message, font=("Segoe UI", 11), bg="#d35400", fg="white")
send_button.pack(pady=(0, 10))

# Bind Enter key
window.bind('<Return>', lambda event: send_message())

# Show welcome message
append_message("DESKTECH", initial_text)

# Run the app
window.mainloop()
