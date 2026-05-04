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
    return psycopg2.connect(DATABASE_URL, sslmode="require")


@app.on_event("startup")
def startup():
    global conn
    conn = get_conn()
    print("DB CONNECTED")


def db():
    return conn.cursor()


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

    cur = db()
    cur.execute("SELECT password FROM players WHERE name=%s", (name,))
    user = cur.fetchone()

    if not user:
        return {"error": "User not found"}

    if user[0] != password:
        return {"error": "Wrong password"}

    conn.commit()
    cur.close()

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

    cur = db()
    cur.execute("UPDATE players SET money = money + 1 WHERE name=%s", (name,))
    conn.commit()
    cur.close()

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

    cur = db()
    cur.execute("INSERT INTO chat (name, message) VALUES (%s, %s)", (name, msg))
    conn.commit()
    cur.close()

    return {"ok": True}


# ---------------- CHAT GET ----------------
@app.get("/chat")
def get_chat():
    cur = db()
    cur.execute("SELECT id, name, message FROM chat ORDER BY id DESC LIMIT 20")
    data = cur.fetchall()
    cur.close()
    return data


# ---------------- TOP ----------------
@app.get("/top")
def top():
    cur = db()
    cur.execute("SELECT name, money FROM players ORDER BY money DESC LIMIT 5")
    data = cur.fetchall()
    cur.close()
    return data