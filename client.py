import requests

BASE = "https://clickergame-41c3.onrender.com"

print("=== CLICKER GAME ===")

# ---------------- LOGIN ----------------
name = input("Username: ")
password = input("Password: ")

r = requests.post(BASE + "/login", json={
    "name": name,
    "password": password
})

token = r.json().get("token")

if not token:
    print("Login failed:", r.json())
    exit()

headers = {"Authorization": "Bearer " + token}

# ---------------- LOOP ----------------
while True:
    print("\nclick | chat | readchat | top | exit")
    cmd = input("> ")

    # CLICK
    if cmd == "click":
        r = requests.post(BASE + "/click", headers=headers)
        print(r.json())

    # CHAT
    elif cmd == "chat":
        msg = input("Message: ")
        r = requests.post(BASE + "/chat", json={"message": msg}, headers=headers)
        print(r.json())

    # READ CHAT
    elif cmd == "readchat":
        r = requests.get(BASE + "/chat")

        for row in reversed(r.json()):
            print(f"{row[1]}: {row[2]}")

    # TOP
    elif cmd == "top":
        r = requests.get(BASE + "/top")
        print(r.json())

    elif cmd == "exit":
        break

    else:
        print("Unknown command")