# Smart Assistant – AI-Powered Pizza Ordering System 🍕

A voice-enabled smart assistant built in Python using Gemini 1.5 Flash API, designed to manage pizza orders through a simple and interactive Tkinter GUI. The assistant supports multiple pizza types, toppings, customizations (halal, allergies), and payment methods, and outputs structured order data (JSON, CSV, or XML).

---

## ✨ Features

- 🔊 Speech input/output interaction (multilingual)
- 🧠 Gemini 1.5 API integration for natural conversation
- 🍕 Fully customizable pizza builder (half-and-half, toppings, dietary filters)
- 📦 Real-time order validation with summary and structured output
- 🧾 Output formats: JSON, CSV, XML
- 💳 Payment method selection (cash, contactless, PayPal)
- 🖼️ Clean Tkinter GUI interface

---

## 🖥️ Tech Stack

- **Python 3.10+**
- **Gemini 1.5 Flash (via Google API)**
- **Tkinter**
- **SpeechRecognition / pyttsx3** (optional for voice)
- **Pandas / JSON / CSV**

---

## 🚀 Setup

```bash
# Clone the repository
git clone https://github.com/Alexayavish/Smart_Assistant.git
cd Smart_Assistant

# Create a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install required dependencies
pip install -r requirements.txt

# Add your Gemini API Key to .env or directly into Main.py
