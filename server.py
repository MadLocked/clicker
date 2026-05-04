from fastapi import FastAPI, Header
import psycopg2
import os
import jwt
import time

app = FastAPI()

SECRET = os.getenv("SECRET", "DEV_SECRET_CHANGE_ME")
DATABASE_URL = os.getenv("DATABASE_URL")

last_click = {}

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

    conn, cur = db_cursor()

    cur.execute(
        "UPDATE players SET money = money + 1 WHERE name=%s",
        (name,)
    )

    conn.commit()
    cur.close()
    conn.close()

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