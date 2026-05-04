import requests

BASE = "https://clickergame-41c3.onrender.com"

print("=== CLICKER GAME ===")

mode = input("login or register: ").strip()

name = input("Username: ")
password = input("Password: ")

# ---------------- REGISTER ----------------
if mode == "register":
    r = requests.post(BASE + "/register", json={
        "name": name,
        "password": password
    })
    print(r.json())
    exit()

# ---------------- LOGIN ----------------
r = requests.post(BASE + "/login", json={
    "name": name,
    "password": password
})

data = r.json()

if not data.get("token"):
    print("Login failed:", data)
    exit()

headers = {"Authorization": "Bearer " + data["token"]}

# ---------------- LOOP ----------------
while True:
    print("\n[ENTER]=click | chat | readchat | top | buy | online | exit")
    cmd = input("> ").strip()

    # CLICK
    if cmd == "":
        r = requests.post(BASE + "/click", headers=headers)
        data = r.json()

        if "error" in data:
            print("❌", data["error"])
        else:
            print(f"+💰 → {data['money']}")

    elif cmd == "chat":
        msg = input("Message: ")
        print(requests.post(
            BASE + "/chat",
            json={"message": msg},
            headers=headers
        ).json())

    elif cmd == "readchat":
        r = requests.get(BASE + "/chat")
        for row in reversed(r.json()):
            print(f"{row['name']}: {row['message']}")

    elif cmd == "top":
        r = requests.get(BASE + "/top")
        for i, p in enumerate(r.json(), 1):
            print(f"{i}. {p['name']} - {p['money']}")

    elif cmd == "buy":
        print(requests.post(BASE + "/buy", headers=headers).json())

    elif cmd == "online":
        data = requests.get(BASE + "/online").json()
        print(f"🟢 Online ({data['count']}):", data["players"])

    elif cmd == "exit":
        break

    else:
        print("Unknown command")