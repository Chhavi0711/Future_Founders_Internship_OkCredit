# Amrit Mattha Billing & Reconciliation App

A lightweight billing and reconciliation web app built for **Amrit Mattha by Bolte Laddoo** ; a Kanpur-based food & beverage retailer established in 1963. Built as part of the **OkCredit Future Founders Internship 2026**.

**Live app:** https://future-founders-internship-okcredit.onrender.com

---

## The Problem

Amrit Mattha was running two disconnected systems : pen-and-paper for cash sales, Paytm for online payments - leading to daily reconciliation errors and 45+ minutes spent tallying sales by hand every day.

## The Solution

A single billing app that logs every sale (cash or UPI) in one place, with a live daily reconciliation view - cutting end-of-day tally from 45 minutes to seconds.

---

## Features

- **Quick billing** : tap-to-add menu items with a live-updating bill and quantity controls
- **Cash / UPI toggle** : every order tagged by payment method at checkout
- **Daily reconciliation dashboard** : cash total, online total, order count, and average bill for any selected date
- **Offline-first** : orders queue locally and auto-sync every 30 seconds when the connection returns, so billing never stops
- **PIN-protected access** : a two-layer PIN lock (first-time setup + returning-user dot-pad) keeps the app secure on a shared device
- **Google Sheets sync** : every order is also pushed to a connected Google Sheet, giving the merchant an independent, exportable copy of his own data

---

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3, Flask, Flask-CORS |
| Database | SQLite |
| Sync | Google Apps Script (Sheets webhook) |
| Hosting | Render.com |

---

## Project Structure

```
amrit-mattha-backend/
├── backend/
│   └── app.py                  # Flask API + SQLite, also serves the frontend
├── frontend/
│   └── index.html               # Full app UI (HTML + CSS + JS)
├── scripts/
│   └── google_sheets_sync.js    # Apps Script webhook for Sheets sync
├── Procfile                     # Render start command
├── requirements.txt
├── .gitignore
├── README.md
└── LICENSE
```

---

## API Reference

| Method | Route | Description |
|---|---|---|
| `GET` | `/api/health` | Server health check |
| `GET` | `/api/menu` | Returns all menu items as JSON |
| `POST` | `/api/orders` | Saves a new bill to SQLite |
| `GET` | `/api/orders?date=YYYY-MM-DD` | Returns all orders for a given date |
| `GET` | `/api/reconcile?date=YYYY-MM-DD` | Returns cash/online/total/count/avg for a given date |

**SQLite schema - `orders` table:**

```
id | order_uid | date | time | total | payment (cash|online) | items_json
```

---

## Running Locally

```bash
# clone the repo
git clone https://github.com/Chhavi0711/amrit-mattha-billing.git
cd amrit-mattha-billing

# install dependencies
pip install -r requirements.txt

# run the server
gunicorn --chdir backend app:app
```

The frontend is served automatically at `/` from `backend/app.py`.

---

## Deploying to Render

1. Fork/clone this repo and push it to your own GitHub account.
2. Create a new **Web Service** on [Render](https://render.com), connecting it to your repo.
3. Set the start command to:
   ```
   gunicorn --chdir backend app:app
   ```
4. Render will pick up `requirements.txt` automatically. Deploy.

> **Note:** Render's free tier uses an ephemeral filesystem - the SQLite database resets on every redeploy or after an inactivity restart. Google Sheets sync and per-device `localStorage` currently provide continuity. For persistent storage, consider migrating to [Railway](https://railway.app) or a hosted Postgres instance (e.g. Supabase).

### Google Sheets Sync Setup

1. Open [Google Apps Script](https://script.google.com) and create a new project.
2. Paste in `scripts/google_sheets_sync.js`.
3. Deploy it as a **Web App** (execute as yourself, accessible to anyone).
4. Copy the deployment URL into the frontend's Sheets sync settings.

---

## Known Issues / Roadmap

- [ ] **API authentication** : `/api/orders` is currently publicly readable by anyone with the URL, even though the app itself is PIN-locked. Adding a shared secret via an `X-API-Key` header (checked in `app.py`) is next up.
- [ ] **Persistent database** : migrate off Render's ephemeral SQLite to Railway or Supabase Postgres.
- [ ] **Server-side PIN** : currently PIN is stored per-device in `localStorage`; a synced, server-side PIN would let the merchant unlock from any device.
- [ ] **Configurable menu** : menu items/prices are currently hardcoded in `index.html`; an admin panel is planned.
- [ ] **Receipt printing** : add thermal printer support (currently receipts are digital-only).


---


## Acknowledgements

Built for Attrey Misra and Amrit Mattha by Bolte Laddoo, as part of the OkCredit Future Founders Internship 2026.
