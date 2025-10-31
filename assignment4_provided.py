from socket import *
import sys
import threading
import os

GOODBYEMSGFILE = "./goodbye.txt"
BEFORELOGINMSGFILE = "./prelogin.txt"
USERS_FILE = "./users.txt"

beforeLoginMsg = ''
goodbyeMsg = ''

users = {} #{ username: password }

def loadMsgs():
    global beforeLoginMsg
    global goodbyeMsg
    
    with open(BEFORELOGINMSGFILE, "r") as f:
        beforeLoginMsg = f.read()
    with open(GOODBYEMSGFILE, "r") as f:
        goodbyeMsg = f.read()

#-----established users-----
def load_users():
    global users
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) == 2:
                users[parts[0]] = parts[1]

def save_users():
    with open(USERS_FILE, "w") as f:
        for u, p in user.items():
            f.write(f"{u}:{p}\n")
                

"""
Send all data to sock, return 1 if successful
-1 if failed (socket error)
"""
def mySendAll(sock, data):
    total_sent = 0
    data_length = len(data)

    try:
        while total_sent < data_length:
            sent = sock.send(data[total_sent:])
            if sent == 0:
                # Socket connection broken
                return -1
            total_sent += sent

    except Exception :
        print("Socket send error in mySendAll.\n")
        return -1

    return 1

def processCmd(userName, sock, cmd):
    print(f"process '{cmd}' from {userName}")
    parts = cmd.split()
    if not parts: 
        return

    command = parts[0].lower()
    #guest can use register, exit, or quit
    if isGuest and command not in ("register", "exit", "quit"):
        mySendAll(sock, b"Guests can only use 'register', 'exit', or 'quit'.\n")
        return
    if command == "register":
        if len(parts) != 3:
            mySendAll(sock, b"Usage: register username password\n")
            return
        uname, pwd = parts[1], parts[2]
        if uname in users:
            mySendAll(sock, b"Username already exists.\n")
        else:
            users[name] = pwd
            save_users()
            mySendAll(sock, f"Registered user '{uname}'.\n".encode())
    else:
        # perform according to the cmd, echo for now
        mySendAll(sock, f"Server response to '{cmd}'\n".encode())

def handleOneClient(sock):

    mySendAll(sock, beforeLoginMsg.encode())
    mySendAll(sock, "Type 'guest', 'login', or 'register': ".encode())
    choice = sock.recv(1000).decode().strip().lower()

    userName = None
    isGuest = False

    if choice == "guest":
        userName = f"guest{len(users)+1}"
        isGuest = True

    elif choice == "register":
        mySendAll(sock, "Enter new username: ".encode())
        uname = sock.recv(1000).decode().strip()
        if uname in users:
            mySendAll(sock, "Username already exists.\n".encode())
            sock.close()
            return
        mySendAll(sock, "Enter password: ".encode())
        pwd = sock.recv(1000).decode().strip()

        users[uname] = pwd
        save_users()
        userName = uname
        mySendAll(sock, f"Registered user '{uname}'\n".encode())

    elif choice == "login":
        mySendAll(sock, "Username: ".encode())
        uname = sock.recv(1000).decode().strip()
        mySendAll(sock, "Password: ".encode())
        pwd = sock.recv(1000).decode().strip()
        if uname in users and users[uname] == pwd:
            userName = uname
            mySendAll(sock, f"Welcome back, {uname}!\n".encode())
        else:
            mySendAll(sock, "Invalid login.\n".encode())
            sock.close()
            return

    else:
        mySendAll(sock, "Invalid option.\n".encode())
        sock.close()
        return

    welcome_banner = """ %%%%% """

    mySendAll(sock, welcome_banner.encode())
    if isGuest:
        mySendAll(sock, "You login as a guest. The only commands that you can use are 'register username password', 'exit', and 'quit'.\n".encode())
    else: 
        mySendAll(sock, f"You are logged in as {userName}.\n".encode())

    str = f"Welcome to the Internet Chat Room, {userName}!\n\n"
    mySendAll(sock, str.encode())

    cmdCount = 0
    mySendAll(sock, f"<{userName}:{cmdCount}> ".encode())
    
    while True:
        data = sock.recv(1000)
        if (len(data) == 0):
            print("Client closed connection")
            sock.close()
            break

        cmd = data.decode().strip()
        command = cmd.split()[0].lower()


        if (command == 'quit' or command == 'exit'):
            mySendAll(sock, goodbyeMsg.encode())
            sock.close()
            break
        else: 
            processCmd(userName, sock, cmd)

        # send prompt
        cmdCount = cmdCount + 1
        mySendAll(sock, f"<{userName}:{cmdCount}> ".encode())


#--main server ---
if len(sys.argv) != 2:
    print("Usage: server_port")
    sys.exit(1)

loadMsgs()
load_users()

s = socket()
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

h = gethostname()
#print(sys.argv[0], sys.argv[1])

s.bind((h, int(sys.argv[1])))
s.listen(5)

print(sys.argv[0], sys.argv[1])
        
while True:
    sock, addr = s.accept()
    print("Receive client connection from ", addr)
    p = threading.Thread(target=handleOneClient, args=(sock,), daemon = True)
    p.start()
    




