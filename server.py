from fastapi import FastAPI, Header
import psycopg2, os, jwt, time

app = FastAPI()

DATABASE_URL = "postgresql://postgres:Sayan_top@db.xxxxx.neon.tech/postgres?sslmode=require"
SECRET = "SUPER_SECRET_KEY_123"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

last_click = {}
last_chat = {}

# ---------------- JWT ----------------
def create_token(name):
    return jwt.encode({"name": name}, SECRET, algorithm="HS256")

def verify(token):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])["name"]
    except:
        return None

# ---------------- LOGS ----------------
def add_log(name, action):
    cur.execute(
        "INSERT INTO logs (name, action) VALUES (%s, %s)",
        (name, action)
    )

# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: dict):
    name = data["name"]
    password = data["password"]

    cur.execute(
        "SELECT password FROM players WHERE name=%s",
        (name,)
    )
    user = cur.fetchone()

    if not user:
        return {"error": "User not found"}

    add_log(name, "login")

    return {"token": create_token(name)}

# ---------------- CLICK ----------------
@app.post("/click")
def click(authorization: str = Header(None)):
    name = verify(authorization.replace("Bearer ", ""))

    if not name:
        return {"error": "Invalid token"}

    now = time.time()
    if name in last_click and now - last_click[name] < 0.3:
        return {"error": "Too fast"}

    last_click[name] = now

    cur.execute(
        "UPDATE players SET money = money + 1 WHERE name=%s",
        (name,)
    )
    conn.commit()

    add_log(name, "click")

    return {"ok": True}

# ---------------- SEND MONEY ----------------
@app.post("/send")
def send(data: dict, authorization: str = Header(None)):
    sender = verify(authorization.replace("Bearer ", ""))

    if not sender:
        return {"error": "Invalid token"}

    receiver = data["to"]
    amount = data["amount"]

    if amount <= 0 or amount > 1000:
        return {"error": "Invalid amount"}

    cur.execute("SELECT money FROM players WHERE name=%s", (sender,))
    sender_money = cur.fetchone()[0]

    if sender_money < amount:
        return {"error": "Not enough money"}

    cur.execute(
        "UPDATE players SET money = money - %s WHERE name=%s",
        (amount, sender)
    )

    cur.execute(
        "UPDATE players SET money = money + %s WHERE name=%s",
        (amount, receiver)
    )

    # 💸 transfers log
    cur.execute("""
        INSERT INTO transfers (from_user, to_user, amount)
        VALUES (%s, %s, %s)
    """, (sender, receiver, amount))

    add_log(sender, f"send {amount} -> {receiver}")

    conn.commit()

    return {"ok": True}

# ---------------- CHAT ----------------
@app.post("/chat")
def chat(data: dict, authorization: str = Header(None)):
    name = verify(authorization.replace("Bearer ", ""))

    if not name:
        return {"error": "Invalid token"}

    msg = data["message"]

    if len(msg) > 200:
        return {"error": "Too long"}

    now = time.time()
    if name in last_chat and now - last_chat[name] < 1:
        return {"error": "Spam"}

    last_chat[name] = now

    cur.execute(
        "INSERT INTO chat (name, message) VALUES (%s, %s)",
        (name, msg)
    )

    add_log(name, "chat")

    conn.commit()

    return {"ok": True}

# ---------------- CHAT GET ----------------
@app.get("/chat")
def get_chat():
    cur.execute("""
        SELECT id, name, message, created_at
        FROM chat
        ORDER BY id DESC
        LIMIT 20
    """)
    return cur.fetchall()

# ---------------- TOP ----------------
@app.get("/top")
def top():
    cur.execute("""
        SELECT name, money
        FROM players
        ORDER BY money DESC
        LIMIT 5
    """)
    return cur.fetchall()

# ---------------- TRANSFERS ----------------
@app.get("/transfers")
def transfers():
    cur.execute("""
        SELECT from_user, to_user, amount, created_at
        FROM transfers
        ORDER BY id DESC
        LIMIT 20
    """)
    return cur.fetchall()

# ---------------- LOGS ----------------
@app.get("/logs")
def logs():
    cur.execute("""
        SELECT name, action, created_at
        FROM logs
        ORDER BY id DESC
        LIMIT 50
    """)
    return cur.fetchall()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)