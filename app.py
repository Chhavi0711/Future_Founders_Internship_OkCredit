from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os, datetime, json, requests

app = Flask(__name__)
CORS(app)

# Your Live Google Sheets Pipeline!
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbzUt9vxKUC8FeC2mrBSbXJkw5JeEgSS5b4UHVG38HX3KOWis5aZD9vmnSaWMDyOGgyAXA/exec"

MENU = [
    # Mattha
    {"id": 1,  "category": "Mattha",             "name": "Masala Mattha",             "price": 25,  "emoji": "🥛"},
    {"id": 2,  "category": "Mattha",             "name": "Masala Mattha with Butter", "price": 35,  "emoji": "🧈"},
    # Lassi
    {"id": 3,  "category": "Lassi",              "name": "Sweet Lassi",               "price": 70,  "emoji": "🍶"},
    {"id": 4,  "category": "Lassi",              "name": "Kesar Lassi",               "price": 70,  "emoji": "🌼"},
    {"id": 5,  "category": "Lassi",              "name": "Mango Lassi",               "price": 70,  "emoji": "🥭"},
    {"id": 6,  "category": "Lassi",              "name": "Strawberry Lassi",          "price": 70,  "emoji": "🍓"},
    # Bread
    {"id": 7,  "category": "Bread",              "name": "Milk Bread",                "price": 30,  "emoji": "🍞"},
    {"id": 8,  "category": "Bread",              "name": "Multigrain Bread",          "price": 30,  "emoji": "🌾"},
    # Buns
    {"id": 9,  "category": "Buns",               "name": "Plain Bun",                 "price": 35,  "emoji": "🥐"},
    {"id": 10, "category": "Buns",               "name": "Sweet Bun",                 "price": 50,  "emoji": "🍯"},
    {"id": 11, "category": "Buns",               "name": "Multigrain Bun",            "price": 50,  "emoji": "🌾"},
    {"id": 12, "category": "Buns",               "name": "Masala Multigrain Bun",     "price": 50,  "emoji": "🌶️"},
    {"id": 13, "category": "Buns",               "name": "Almond Bun",                "price": 50,  "emoji": "🌰"},
    {"id": 14, "category": "Buns",               "name": "Strawberry Bun",            "price": 60,  "emoji": "🍓"},
    {"id": 15, "category": "Buns",               "name": "Pineapple Bun",             "price": 60,  "emoji": "🍍"},
    {"id": 16, "category": "Buns",               "name": "Blueberry Bun",             "price": 60,  "emoji": "🫐"},
    {"id": 17, "category": "Buns",               "name": "Mango Bun",                 "price": 60,  "emoji": "🥭"},
    {"id": 18, "category": "Buns",               "name": "Cheesecake Bun",            "price": 60,  "emoji": "🍰"},
    {"id": 19, "category": "Buns",               "name": "Pizza Bun",                 "price": 80,  "emoji": "🍕"},
    # Flavoured Yogurt
    {"id": 20, "category": "Flavoured Yogurt",   "name": "Strawberry Yogurt",         "price": 70,  "emoji": "🍓"},
    {"id": 21, "category": "Flavoured Yogurt",   "name": "Mango Yogurt",              "price": 70,  "emoji": "🥭"},
    {"id": 22, "category": "Flavoured Yogurt",   "name": "Blueberry Yogurt",          "price": 70,  "emoji": "🫐"},
]

# Set Timezone to IST (GMT+5:30)
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

@app.route("/")
def home():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "index.html")
    if os.path.exists(html_path):
        return send_file(html_path)
    return f"<h1>Error: index.html not found!</h1><p>I am looking exactly here: {html_path}</p>", 404

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "app": "Amrit Mattha Billing API connected to Google Sheets"})

@app.route("/api/menu")
def get_menu():
    return jsonify(MENU)

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.json
    if not data:
        return jsonify({"error": "No data"}), 400
        
    raw_payment = str(data.get("payment", "")).lower()
    clean_payment = "online" if "upi" in raw_payment or "online" in raw_payment or "paytm" in raw_payment else "cash"

    # Force the timestamp to strictly use Local IST
    ist_time = datetime.datetime.now(IST).strftime("%Y-%m-%d %I:%M %p")

    payload = {
        "id": str(data.get("id", "N/A")),
        "time": ist_time,
        "total": int(data.get("total", 0)),
        "payment": clean_payment,
        "items": data.get("items", [])
    }

    try:
        requests.post(GOOGLE_SHEET_URL, json=payload)
        return jsonify({"status": "saved_to_sheets"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RESTORED: The endpoint that feeds the Order Log UI
@app.route("/api/orders", methods=["GET"])
def get_orders():
    try:
        response = requests.get(GOOGLE_SHEET_URL)
        return jsonify(response.json())
    except:
        return jsonify([])

@app.route("/api/reconcile")
def reconcile():
    try:
        response = requests.get(GOOGLE_SHEET_URL)
        rows = response.json()
        
        cash = sum(int(r.get("total", 0)) for r in rows if r.get("payment") == "cash")
        online = sum(int(r.get("total", 0)) for r in rows if r.get("payment") == "online")
        count = len(rows)
        total = cash + online
        
        return jsonify({
            "date": datetime.datetime.now(IST).strftime("%Y-%m-%d"),
            "cash": cash,
            "online": online,
            "total": total,
            "orders": count, # Restored to a simple integer to fix the frontend crash
            "avg_bill": round(total/count) if count else 0
        })
    except Exception as e:
        return jsonify({"cash": 0, "online": 0, "total": 0, "orders": 0, "avg_bill": 0})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
