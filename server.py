import socket
import threading
import sys
from User import UserClient
from datetime import datetime
import Message
import time
import db_controller
from passlib.hash import pbkdf2_sha256

clients = set()
clients_lock = threading.Lock()
online_users = []
user_sockets = {}
BUFFER_SIZE = 8192
SOCK_LISTEN_SIZE = 10


def create_socket():
    """
    First creating the server socket, binding the host and port to it,
    then making it listen for any incoming client connections and when the
    connection comes in, create a thread for it.
    """
    host = '192.168.101.72'
    port = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(SOCK_LISTEN_SIZE)
    print("Server setup")

    while True:
        conn, address = sock.accept()
        print(address, "has connected to the server")
        threading.Thread(target=begin_authentication, args=(conn, address)).start()


def begin_authentication(client_socket, address):

    with clients_lock:
        if client_socket not in clients:
            clients.add(client_socket)

    while True:

        try:
            data = client_socket.recv(BUFFER_SIZE)
        except OSError:
            "Client disconnected auth check"
            sys.exit(0)

        if data is not None:
            data_read = data
            data_decoded = data_read.decode('utf-8')

            if data_decoded.startswith('/login'):
                wrap_and_send_message(client_socket, "login")
                user_login(client_socket, address)

            elif data_decoded == '/create':
                wrap_and_send_message(client_socket, "create")
                create_user(client_socket, address)

            elif data_decoded == 'closing':
                pass

            else:
                pass


def new_client(client_socket, address, client_user, online_user_list, online_status):
    """
    Add the client to a list of clients then waits to receive data. When the data
    comes in, it is sent to everyone who didn't send the message. Also handles the
    user requesting to do things such as adding friends.
    """
    print("{0} logged in".format(client_user.username))
    recent = Message.show_recent_messages(client_socket)
    dm = Message.show_direct_messages(client_socket, client_user.username)

    wrap_and_send_message(client_socket, recent)
    wrap_and_send_message(client_socket, dm)

    friend_online_message = "Your friend {0} has joined the server! \n".format(client_user.username)
    friend_broadcast(client_user.username, friend_online_message)
    
    while online_status is True:

        try:
            data = client_socket.recv(BUFFER_SIZE)
            data_decoded = data.decode('utf-8')
        except OSError:
            "Client disconnected receive check"
            online_status = False
            client_disconnects(client_user, client_socket)
            sys.exit(0)

        while data_decoded is not None:
            data_decoded = data.decode('utf-8')
            
            if data_decoded == '/delete':
                online_users.remove(client_user.username)
                delete_user(client_socket, client_user.username, address)           
            
            elif data_decoded == '/online':
                show_online_users(client_socket, online_user_list) 

            elif data_decoded == '/users':
                show_all_users(client_socket)

            elif data_decoded == '/friends':
                show_friends(client_socket, client_user.username)
        
            elif data_decoded.startswith("/dm"):
                target = data_decoded[4:]
                user_check = db_controller.check_user(target)

                if target in online_users:
                    direct_message(client_socket, client_user.username, user_sockets, target)

                elif target not in online_users and target == user_check:

                    data = client_socket.recv(BUFFER_SIZE)
                    data = data.decode('utf-8')

                    db_controller.save_direct_message_to_db(client_user.username, data, target)
         
            if data_decoded.startswith("/add"):
                target_friend = data_decoded[5:]
                message = UserClient.add_friend(client_user, target_friend)
                if message == "/success":
                    client_user.friends.append(target_friend)
                print(message)

                wrap_and_send_message(client_socket, message)

            elif data_decoded.startswith('/remove'):
                target = data_decoded[8:]
                message = UserClient.remove_friend(client_user, target)
                if message == "{0} has been removed from your friend list".format(target):
                    client_user.friends.remove(target)

                wrap_and_send_message(client_socket, message)
            
                          
            elif data_decoded == '/exit':
                online_status = False
                client_disconnects(client_user, client_socket)
                wrap_and_send_message(client_socket, "/exit")
                print("{0} has logged out".format(client_user.username))
            
            print(client_user.username, ": ", data)

            if not data_decoded.startswith("/"):
                db_controller.save_server_message_to_db(client_user.username, data_decoded)
                broadcast_message(client_socket, client_user.username, data_decoded)

            break
    begin_authentication(client_socket, address)


def wrap_and_send_message(client_socket, message):
    message_to_send = message.encode('utf-8')
    client_socket.send(message_to_send)


def client_disconnects(client_user, client_socket):
    # Lets friends of the user disconnecting they have disconnected

    message = "{0} has disconnected from the server \n".format(client_user.username)
    friend_broadcast(client_user.username, message)

    online_users.remove(client_user.username)
    with clients_lock:
        clients.remove(client_socket)

    del client_user


def friend_broadcast(username, message):

    all_friends = db_controller.get_user_added(username)
    friend_keys = []
    for friend in all_friends:
        friend_keys.append(friend)
    print(friend_keys)

    for name, user_socket in user_sockets.items():
        if name in friend_keys:
            try:
                user_sockets.get(name).send(message.encode('utf-8'))
            except ConnectionResetError:
                print("Client disconnected friend broadcast check")
            except OSError:
                print("Client disconnected")


def broadcast_message(client_socket, username, data):
    with clients_lock:
        for c in clients:
            try:
                now = datetime.now()
                time = now.strftime("%H:%M")
                c.send("{0} ({1}): {2} \n".format(username, time, data).encode('utf-8'))
            except ConnectionResetError:
                print("Client disconnected message broadcast check")
            except OSError:
                print("Client disconnected")


def user_login(client_socket, address):

    while True:
        data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
        name = data.lower()

        name_check = db_controller.check_user(name)

        if name == name_check and name not in online_users:
            wrap_and_send_message(client_socket, "accepted")

            password = db_controller.return_password(name)
            data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
            print(data)

            if check_password(password, data) is True:
                online_users.append(name)
                print(online_users)
                online_status = True

                user_sockets[name] = client_socket

                wrap_and_send_message(client_socket, "logged ")
                identifier = db_controller.get_user_id(name)
                friends = db_controller.show_all_friends(name)
                print(friends)

                client_user = UserClient(name, identifier, password, friends)

                new_client(client_socket, address, client_user, online_users, online_status)
            else:
                print("login failed")
                wrap_and_send_message(client_socket, "passfail")
                begin_authentication(client_socket, address)

        elif name in online_users:
            print("online")
            wrap_and_send_message(client_socket, "denied")
            begin_authentication(client_socket, address)

        else:
            print("error")
            wrap_and_send_message(client_socket, "error")
            begin_authentication(client_socket, address)


def create_user(client_socket, address):

    while True:
        data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
        name = data.lower()

        if data == "closing":
            print("closing")
            begin_authentication(client_socket, address)

        name_check = db_controller.check_user(name)
        print(name_check)

        if name == '/login':
            begin_authentication(client_socket, address)

        if name_check == "p":
            wrap_and_send_message(client_socket, "pass")
            break
        
        elif name == name_check:
            wrap_and_send_message(client_socket, "error")

    password = client_socket.recv(BUFFER_SIZE).decode('utf-8')
    password_two = client_socket.recv(BUFFER_SIZE).decode('utf-8')

    if password == password_two:
        hashed_password = hash_password(password)

        max_id = db_controller.return_last_user_id()
        identifier = max_id + 1

        db_controller.add_user_to_db(name, identifier, hashed_password)
        print("accountmade")
        wrap_and_send_message(client_socket, "success")

    if password != password_two:
        wrap_and_send_message(client_socket, "fail")
        create_user(client_socket, address)

    begin_authentication(client_socket, address)


def delete_user(client_socket, username, address):

    db_controller.delete_user_from_db(username)
    db_controller.delete_user_from_friend_db(username)
    wrap_and_send_message(client_socket, "/exit")

    begin_authentication(client_socket, address)


def hash_password(password):
    return pbkdf2_sha256.hash(password)


def check_password(hashed_password, input_password):
    return pbkdf2_sha256.verify(input_password, hashed_password)


def direct_message(client_socket, username, sockets, target):

    data = client_socket.recv(BUFFER_SIZE)
    data_to_send = "(PM) {0} says: {1}".format(username, data.decode('utf-8'))

    try:
        sockets.get(target).send(data_to_send.encode('utf-8'))
    except ConnectionResetError:
        print("Client disconnected dm check")
    except OSError:
        print("Client disconnected")


def show_online_users(client_socket, online_user_list):

    online_message = '/online '
    for user in online_user_list:
        online_message += user + ', '

    wrap_and_send_message(client_socket, online_message)


def show_all_users(client_socket):

    all_users = db_controller.get_all_users()
    user_message = '/users '

    for user in all_users:
        user_message += user + ', '
        
    wrap_and_send_message(client_socket, user_message)


def show_friends(client_socket, username):

    friend_list = db_controller.show_all_friends(username)
    friend_message = '/friends '

    for user in friend_list:
        friend_message += user + ', '

    wrap_and_send_message(client_socket, friend_message)


if __name__ == '__main__':
    create_socket()

