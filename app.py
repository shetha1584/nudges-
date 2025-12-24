from flask import Flask, request
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Use environment variable, fallback to your external URL for local testing
DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://nudges_user:VFCoC8yTf5DALTSKdZQaRwZmVwfboZJE@dpg-d55nuj4hg0os73a7s4ig-a.oregon-postgres.render.com/nudges"
)

# Optional: create table if it doesn't exist
def ensure_table():
    with psycopg2.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS load_shift_responses (
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER NOT NULL,
                    shift_percent INTEGER NOT NULL,
                    response_time TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """)
            conn.commit()

ensure_table()

def save_response(client_id, shift):
    try:
        client_id = int(client_id)
        shift = int(shift)
    except (ValueError, TypeError):
        return False, "Invalid client_id or shift value"

    try:
        with psycopg2.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO load_shift_responses (client_id, shift_percent, response_time)
                    VALUES (%s, %s, %s)
                """, (client_id, shift, datetime.utcnow()))
                conn.commit()
        return True, None
    except Exception as e:
        print("DB Error:", e)
        return False, str(e)

@app.route("/track")
def track():
    client_id = request.args.get("client_id")
    shift = request.args.get("shift")

    success, error = save_response(client_id, shift)
    if not success:
        return f"❌ Error recording response: {error}", 400

    return f"""
    <html>
      <body style="font-family: Arial; text-align:center; margin-top:60px;">
        <h2>✅ Response Recorded</h2>
        <p>{shift}% load shift confirmed.</p>
      </body>
    </html>
    """

@app.route("/")
def home():
    return "Server running ✅"

if __name__ == "__main__":
    # Only for local testing
    app.run(host="0.0.0.0", port=5000, debug=True)
