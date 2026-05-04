import requests

BASE = "https://clickergame-41c3.onrender.com"

print("=== CLICKER GAME ===")

# ---------------- MODE ----------------
mode = input("Type 'login' or 'register': ").strip().lower()

name = input("Username: ")
password = input("Password: ")

# ---------------- REGISTER ----------------
if mode == "register":
    try:
        r = requests.post(BASE + "/register", json={
            "name": name,
            "password": password
        })
        data = r.json()
    except:
        print("Server error")
        exit()

    if data.get("error"):
        print("Register failed:", data["error"])
        exit()

    print("Registered successfully! Now login again.")
    exit()


# ---------------- LOGIN ----------------
try:
    r = requests.post(BASE + "/login", json={
        "name": name,
        "password": password
    })

    data = r.json()
except:
    print("Server error")
    exit()

token = data.get("token")

if not token:
    print("Login failed:", data)
    exit()

headers = {"Authorization": "Bearer " + token}


# ---------------- LOOP ----------------
while True:
    print("\n[ENTER]=click | chat | readchat | top | buy | online | exit")
    cmd = input("> ").strip()

    # ---------------- ENTER = CLICK ----------------
    if cmd == "":
        r = requests.post(BASE + "/click", headers=headers)
        data = r.json()

        # если клик не прошёл
        if "error" in data:
            print("❌", data["error"])
            continue
        else:
            print("💰", data["money"])
        continue

    # ---------------- COMMANDS ----------------
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
        r = requests.post(BASE + "/buy", headers=headers)
        print(r.json())

    elif cmd == "online":
        r = requests.get(BASE + "/online")
        print("Online:", r.json())

    elif cmd == "exit":
        break

    else:
        print("Unknown command")