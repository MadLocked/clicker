import requests

BASE = "https://clickergame-41c3.onrender.com"

print("=== CLICKER GAME ===")

# ---------------- LOGIN ----------------
name = input("Username: ")
password = input("Password: ")

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
    print("\nclick | chat | readchat | top | exit")
    cmd = input("> ")

    if cmd == "click":
        print(requests.post(BASE + "/click", headers=headers).json())

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

    elif cmd == "exit":
        break

    else:
        print("Unknown command")