import socket
import threading
import sys

host = '192.168.101.88'
port = 5000

print("test1")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
print("test2")

# TODO: prevent user overloading server with information


def login():

    log = input("Type /login to log into an account, or /create to create an account: ")
    login_input = log.encode('utf-8')  # clean up confusing variables with c# client

    client_socket.send(login_input)
    response = client_socket.recv(1024).decode('utf-8')

    if response == 'create':
        create()
    elif response == 'fail':
        login()
    elif response == 'login':
        pass

    user = input("Enter your username: ")
    user_login = user.encode('utf-8')
    client_socket.send(user_login)

    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if data == 'denied':
            print("User is already logged in")
            login()
        elif data == 'accepted':
            password = input("Now enter your password: ")
            client_socket.send(password.encode('utf-8'))  # TODO: hash password before sending in c# client

            data = client_socket.recv(1024).decode('utf-8')
            if data == 'logged':
                print("Logged in.")
                send()
            elif data == 'passfail':
                print("Incorrect password.")
                login()

        elif data == 'error':
            print("Account does not exist")
            login()


def create():

    while True:
        create_input = input("Enter the name you would like to use for your account, or type -- to cancel: ")
        message = create_input.encode('utf-8')
        client_socket.send(message)

        if create_input == '--':
            login()

        data = client_socket.recv(1024).decode('utf-8')
        if data == 'error':
            print("Account already exists, try another name.")
        elif data == 'pass':
            password = input("Now choose a password: ")
            client_socket.send(password.encode('utf-8'))
            print("Account created!")
            login()


def delete():
    delete_input = input("Are you sure you want to delete your account? y/n: ")
    message = delete_input.encode('utf-8')

    client_socket.send(message)

    if delete_input == 'y':
        print("Account deleted")

    login()

    # TODO: fix it breaking when logging in after deleting account


def recv():
    """
    Waits for any incoming data from the server, unpacks it to find out who sent it, and prints
    out the message to the client with the name of the sender and a timestamp.
    """
    while True:
        data = client_socket.recv(1024)
        if data is not None:
            try:
                if data.decode('utf-8') == 'exit':
                    sys.exit(0)
                else:
                    print(data.decode('utf-8'))
            except UnicodeDecodeError:
                pass


def send():
    """
    Allows the user to input their message, packs it up for the server and sends the message to the
    server. Also allows the user to exit or delete their account.
    """
    threading.Thread(target=recv).start()

    message = input("-> ")

    client_socket.send(message.encode('utf-8'))

    while message != '/exit' and message != '/delete':
        message = input("-> ")

        client_socket.send(message.encode('utf-8'))

    if message == '/delete':
        delete()

    if message == '/exit':
        client_socket.send(''.encode('utf-8'))
        print("Logged out.")
        login()


if __name__ == '__main__':
    login()
