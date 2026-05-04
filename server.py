from fastapi import FastAPI, Header
import psycopg2
import os
import jwt
import time

app = FastAPI()

SECRET = os.getenv("SECRET", "DEV_SECRET_CHANGE_ME")
DATABASE_URL = os.getenv("DATABASE_URL")

last_click = {}
online = {}

# ---------------- DB ----------------
def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def db_cursor():
    conn = get_conn()
    return conn, conn.cursor()


# ---------------- JWT ----------------
def create_token(name):
    return jwt.encode({"name": name}, SECRET, algorithm="HS256")


def verify(token):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])["name"]
    except:
        return None


# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: dict):
    name = data["name"]
    password = data["password"]

    conn, cur = db_cursor()

    cur.execute("SELECT password FROM players WHERE name=%s", (name,))
    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        return {"error": "User not found"}

    if user[0] != password:
        cur.close()
        conn.close()
        return {"error": "Wrong password"}

    cur.close()
    conn.close()

    return {"token": create_token(name)}


# ---------------- REGISTER ----------------
@app.post("/register")
def register(data: dict):
    name = data["name"]
    password = data["password"]

    conn, cur = db_cursor()

    cur.execute("SELECT name FROM players WHERE name=%s", (name,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return {"error": "User already exists"}

    cur.execute(
        "INSERT INTO players (name, password) VALUES (%s, %s)",
        (name, password)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {"ok": True}


# ---------------- CLICK ----------------
@app.post("/click")
def click(authorization: str = Header(None)):
    name = verify(authorization.replace("Bearer ", ""))

    if not name:
        return {"error": "Invalid token"}

    online[name] = time.time()

    now = time.time()
    if name in last_click and now - last_click[name] < 0.3:
        return {"error": "Too fast"}

    last_click[name] = now

    conn, cur = db_cursor()

    cur.execute(
        "UPDATE players SET money = money + multiplier WHERE name=%s",
        (name,)
    )

    cur.execute(
        "SELECT money FROM players WHERE name=%s",
        (name,)
    )

    money = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return {"ok": True, "money": money}


# ---------------- BUY ----------------
@app.post("/buy")
def buy(authorization: str = Header(None)):
    name = verify(authorization.replace("Bearer ", ""))

    if not name:
        return {"error": "Invalid token"}

    conn, cur = db_cursor()

    cur.execute("SELECT money, multiplier FROM players WHERE name=%s", (name,))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return {"error": "User not found"}

    money, mult = row
    cost = (mult ** 2) * 2

    if money < cost:
        cur.close()
        conn.close()
        return {"error": f"Need {cost}"}

    new_money = money - cost
    new_mult = mult + 1

    cur.execute(
        "UPDATE players SET money=%s, multiplier=%s WHERE name=%s",
        (new_money, new_mult, name)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {"ok": True, "multiplier": new_mult, "money": new_money}


# ---------------- CHAT ----------------
@app.post("/chat")
def chat(data: dict, authorization: str = Header(None)):
    name = verify(authorization.replace("Bearer ", ""))

    if not name:
        return {"error": "Invalid token"}

    msg = data["message"]

    if len(msg) > 200:
        return {"error": "Too long"}

    conn, cur = db_cursor()

    cur.execute(
        "INSERT INTO chat (name, message) VALUES (%s, %s)",
        (name, msg)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {"ok": True}


# ---------------- CHAT GET ----------------
@app.get("/chat")
def get_chat():
    conn, cur = db_cursor()

    cur.execute(
        "SELECT id, name, message FROM chat ORDER BY id DESC LIMIT 20"
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {"id": r[0], "name": r[1], "message": r[2]}
        for r in rows
    ]


# ---------------- TOP ----------------
@app.get("/top")
def top():
    conn, cur = db_cursor()

    cur.execute(
        "SELECT name, money FROM players ORDER BY money DESC LIMIT 5"
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {"name": r[0], "money": r[1]}
        for r in rows
    ]


# ---------------- ONLINE ----------------
@app.get("/online")
def get_online():
    now = time.time()

    players = [
        name for name, t in online.items()
        if now - t < 10
    ]

    return {
        "count": len(players),
        "players": players
    }