from fastapi import FastAPI, Header
import psycopg2
import os
import jwt
import time

app = FastAPI()

SECRET = "SUPER_SECRET_KEY_123"
DATABASE_URL = os.getenv("DATABASE_URL")

last_click = {}
last_chat = {}

conn = None


# ---------------- DB ----------------
def get_conn():
    return psycopg2.connect(DATABASE_URL)


@app.on_event("startup")
def startup():
    global conn
    try:
        conn = get_conn()
        print("DB CONNECTED")
    except Exception as e:
        print("DB ERROR:", e)
        conn = None


# ---------------- JWT ----------------
def create_token(name):
    return jwt.encode({"name": name}, SECRET, algorithm="HS256")


def verify(token):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])["name"]
    except:
        return None


# ---------------- DB HELPER ----------------
def db_exec(query, params=None, fetch=False):
    if not conn:
        return None

    try:
        cur = conn.cursor()
        cur.execute(query, params or ())

        if fetch:
            data = cur.fetchall()
            cur.close()
            return data

        conn.commit()
        cur.close()
        return True

    except Exception as e:
        print("DB ERROR:", e)
        return None


# ---------------- LOGS ----------------
def add_log(name, action):
    db_exec(
        "INSERT INTO logs (name, action) VALUES (%s, %s)",
        (name, action)
    )


# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: dict):
    name = data["name"]

    user = db_exec(
        "SELECT password FROM players WHERE name=%s",
        (name,),
        fetch=True
    )

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

    db_exec(
        "UPDATE players SET money = money + 1 WHERE name=%s",
        (name,)
    )

    add_log(name, "click")

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

    db_exec(
        "INSERT INTO chat (name, message) VALUES (%s, %s)",
        (name, msg)
    )

    add_log(name, "chat")

    return {"ok": True}


# ---------------- GET CHAT ----------------
@app.get("/chat")
def get_chat():
    return db_exec("""
        SELECT id, name, message, created_at
        FROM chat
        ORDER BY id DESC
        LIMIT 20
    """, fetch=True)


# ---------------- TOP ----------------
@app.get("/top")
def top():
    return db_exec("""
        SELECT name, money
        FROM players
        ORDER BY money DESC
        LIMIT 5
    """, fetch=True)