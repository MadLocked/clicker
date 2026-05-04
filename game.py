import psycopg2
import bcrypt

DATABASE_URL = "postgresql://postgres:Sayan_top@db.xxxxx.neon.tech/postgres?sslmode=require"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
user_name = ''
main_password = ''
def login(name, password):
    cur.execute("SELECT password FROM players WHERE name = %s", (name,))
    user = cur.fetchone()

    if not user:
        print("User not found")
        return

    stored_hash = user[0]

    if isinstance(stored_hash, memoryview):
        stored_hash = stored_hash.tobytes()
    elif isinstance(stored_hash, str):
        stored_hash = stored_hash.encode()

    if bcrypt.checkpw(password.encode(), stored_hash):
        print("Login successful!")
        user_name = name
        main_password = password
    else:
        print("Invalid credentials")

def register(name, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cur.execute("""
    INSERT INTO players (name, password)
    VALUES (%s, %s)
    ON CONFLICT (name) DO NOTHING
    """, (name, hashed_password))

    conn.commit()

    if cur.rowcount == 1:
        print("User created!")
        user_name = name
        main_password = password
    else:
        print("User already exists!")

def click(ret, name):
    if ret == '':
        print('+')
        cur.execute("UPDATE players SET money = money + 1 WHERE name = %s",(name,))
        conn.commit()
    else:
        print('Invalid command')

def send(to_whom):
    amount = int(input('Choose amount of money to send: '))
    if cur.execute('SELECT money FROM players WHERE name = %s', (user_name,)):
        print('Not enough money')
    else:
        cur.execute('UPDATE players SET money = money + %s WHERE name = %s', (amount, to_whom))
        cur.execute('UPDATE players SET money = money - %s WHERE name = %s', (amount, user_name))
        conn.commit()


#Start of cycle

while True:
    print("\n1 - Login")
    print("2 - Register")
    print("3 - Exit")

    h = input("> ")

    if h == '1':
        name = input('Enter your username: ')
        password = input('Enter your password: ')
        login(name, password)

    elif h == '2':
        name = input('Enter your desired username: ')
        password = input('Enter your desired password: ')
        register(name, password)
    
    elif h == '3':
        break

    else:
        print('Invalid command')
    
    print("\n1 - Clicker")
    print("2 - Send money")
    print("3 - Chat")
    print("4 - Exit")
    
    h2 = input("> ")

    if h2 == '1':
        print('Tap enter to get a coin')
        c = input()
        click(c, user_name)
    
    elif h2 == '2':
        send_user = input('Choose user to send money to: ')
        send(send_user)

cur.close()
conn.close()