import requests

BASE = "https://clickergame-41c3.onrender.com"

# ---------------- LOGIN ----------------
name = input("Username: ")
password = input("Password: ")

r = requests.post(BASE + "/login", json={
    "name": name,
    "password": password
})

token = r.json().get("token")

if not token:
    print("Login failed")
    exit()

headers = {"Authorization": "Bearer " + token}

# ---------------- GAME LOOP ----------------
while True:
    print("\nclick | send | chat | readchat | top | exit")
    cmd = input("> ")

    # CLICK
    if cmd == "click":
        r = requests.post(BASE + "/click", headers=headers)
        print(r.json())

    # SEND MONEY
    elif cmd == "send":
        to = input("To: ")
        amount = int(input("Amount: "))

        r = requests.post(BASE + "/send", json={
            "to": to,
            "amount": amount
        }, headers=headers)

        print(r.json())

    # CHAT SEND
    elif cmd == "chat":
        msg = input("Message: ")

        r = requests.post(BASE + "/chat", json={
            "message": msg
        }, headers=headers)

        print(r.json())

    # CHAT READ
    elif cmd == "readchat":
        r = requests.get(BASE + "/chat")

        for row in reversed(r.json()):
            id, n, msg, t = row
            print(f"[{t}] {n}: {msg}")

    # TOP
    elif cmd == "top":
        r = requests.get(BASE + "/top")
        print(r.json())

    # EXIT
    elif cmd == "exit":
        break

    else:
        print("Unknown command")