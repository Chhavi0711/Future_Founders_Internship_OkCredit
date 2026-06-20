"""
Amrit Mattha — Backend API
Flask + SQLite. Serves the frontend HTML AND the API.
Run: python app.py
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3, os, datetime, json

# Tell Flask: the frontend/ folder is where our HTML lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

DB_PATH = os.path.join(BASE_DIR, "amrit_mattha.db")

# ── DB setup ──────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                order_uid TEXT    NOT NULL,
                date      TEXT    NOT NULL,
                time      TEXT    NOT NULL,
                total     INTEGER NOT NULL,
                payment   TEXT    NOT NULL CHECK(payment IN ('cash','online')),
                items_json TEXT   NOT NULL
            )
        """)
        conn.commit()
    print("✅ Database ready:", DB_PATH)

# ── Serve the frontend app ────────────────────────────────────────────────────
@app.route('/')
def index():
    # This sends frontend/index.html to whoever visits the root URL
    return send_from_directory(FRONTEND_DIR, 'index.html')

# ── Menu ──────────────────────────────────────────────────────────────────────
MENU = [
    {"id": 1,  "category": "Beverages",       "name": "Masala Chaas",              "price": 30,  "emoji": "🥛"},
    {"id": 2,  "category": "Beverages",       "name": "Masala Chaas + Butter",     "price": 35,  "emoji": "🧈"},
    {"id": 3,  "category": "Beverages",       "name": "Chaas (1 Litre)",           "price": 80,  "emoji": "🫙"},
    {"id": 4,  "category": "Snacks (Breads)", "name": "Plain Bread + Butter",      "price": 30,  "emoji": "🍞"},
    {"id": 5,  "category": "Snacks (Breads)", "name": "Multigrain Bread + Butter", "price": 30,  "emoji": "🌾"},
    {"id": 6,  "category": "Snacks (Buns)",   "name": "Plain Bun + Butter",        "price": 40,  "emoji": "🥐"},
    {"id": 7,  "category": "Snacks (Buns)",   "name": "Sweet Bun + Butter",        "price": 60,  "emoji": "🍯"},
    {"id": 8,  "category": "Snacks (Buns)",   "name": "Multigrain Bun + Butter",   "price": 60,  "emoji": "🌾"},
    {"id": 9,  "category": "Snacks (Buns)",   "name": "Masala Multigrain Bun",     "price": 60,  "emoji": "🌶️"},
    {"id": 10, "category": "Snacks (Buns)",   "name": "Almond Bun + Butter",       "price": 60,  "emoji": "🌰"},
    {"id": 11, "category": "Snacks (Buns)",   "name": "Mango Bun + Crush",         "price": 60,  "emoji": "🥭"},
    {"id": 12, "category": "Snacks (Buns)",   "name": "Pineapple Bun + Crush",     "price": 60,  "emoji": "🍍"},
    {"id": 13, "category": "Dairy Fresh",     "name": "White Butter (1 kg)",       "price": 600, "emoji": "🧈"},
]

# ── API Routes ────────────────────────────────────────────────────────────────
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "app": "Amrit Mattha Billing API"})

@app.route("/api/menu")
def get_menu():
    return jsonify(MENU)

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.json
    if not data or not all(k in data for k in ["id","time","items","total","payment"]):
        return jsonify({"error": "Missing fields"}), 400
    date_str = data["time"][:10]
    with get_db() as conn:
        conn.execute("""
            INSERT INTO orders (order_uid, date, time, total, payment, items_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (str(data["id"]), date_str, data["time"],
              int(data["total"]), data["payment"], json.dumps(data["items"])))
        conn.commit()
    return jsonify({"status": "saved"}), 201

@app.route("/api/orders")
def get_orders():
    date_str = request.args.get("date", datetime.date.today().isoformat())
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM orders WHERE date = ? ORDER BY time ASC", (date_str,)
        ).fetchall()
    return jsonify([{
        "id": r["order_uid"], "time": r["time"],
        "total": r["total"], "payment": r["payment"],
        "items": json.loads(r["items_json"])
    } for r in rows])

@app.route("/api/reconcile")
def reconcile():
    date_str = request.args.get("date", datetime.date.today().isoformat())
    with get_db() as conn:
        rows = conn.execute(
            "SELECT payment, total FROM orders WHERE date = ?", (date_str,)
        ).fetchall()
    cash   = sum(r["total"] for r in rows if r["payment"] == "cash")
    online = sum(r["total"] for r in rows if r["payment"] == "online")
    count  = len(rows)
    total  = cash + online
    return jsonify({"date": date_str, "cash": cash, "online": online,
                    "total": total, "orders": count,
                    "avg_bill": round(total/count) if count else 0})

@app.route("/")
def home():
    """This is the front door. It serves the index.html file."""
    import os
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: index.html not found!</h1>", 404

if __name__ == "__main__":
    init_db()
    print("🚀 Open the app at: http://localhost:5000")
    print("📱 For phone on same Wi-Fi, use: http://YOUR_LAPTOP_IP:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)