import socket
import time
from time import ctime
import json
import string
import random
import db_controller

# TODO: be able to run in succession
# @james not every test works right now, will fix the remaining ones soon


def rand_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(11))


def calum_login(sock1):
    login_input = '/login'
    user_input = 'calum'
    pass_input = 'test'

    sock1.send(login_input.encode('utf-8'))
    sock1.recv(1024)
    time.sleep(0.1)
    sock1.send(user_input.encode('utf-8'))
    sock1.recv(1024)
    time.sleep(0.1)
    sock1.send(pass_input.encode('utf-8'))
    time.sleep(0.1)

    return sock1


def joe_login(sock2):
    login_input = '/login'
    user_input = 'joe'
    pass_input = 'test'

    sock2.send(login_input.encode('utf-8'))
    sock2.recv(1024)
    time.sleep(0.1)
    sock2.send(user_input.encode('utf-8'))
    sock2.recv(1024)
    time.sleep(0.1)
    sock2.send(pass_input.encode('utf-8'))
    time.sleep(0.1)

    return sock2


def test_valid_login():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    calum_login(sock1)
    data = sock1.recv(1024).decode('utf-8')
    print(data)
    sock1.send("/exit".encode('utf-8'))
    time.sleep(0.1)
    sock1.close()
    return True if data.startswith('logged') else False


def test_invalid_login_user_online():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    calum_login(sock1)

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('192.168.56.1', 5000))

    login_input = '/login'
    user_input = 'calum'

    time.sleep(0.5)
    sock2.send(login_input.encode('utf-8'))
    time.sleep(0.1)
    sock2.recv(1024)
    sock2.send(user_input.encode('utf-8'))
    data = sock2.recv(1024).decode('utf-8')
    print(data)

    sock1.send("/exit".encode('utf-8'))
    time.sleep(0.1)
    sock1.close()
    sock2.close()

    return True if data == 'denied' else False


def test_invalid_login_account_doesnt_exist():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.56.1', 5000))

    login_input = '/login'
    user_input = 'heghegdfg'

    sock.send(login_input.encode('utf-8'))
    time.sleep(0.1)
    sock.recv(1024)
    sock.send(user_input.encode('utf-8'))

    data = sock.recv(1024).decode('utf-8')
    sock.close()

    return True if data == 'error' else False


def test_logout_and_login():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.56.1', 5000))

    exit_input = '/exit'

    calum_login(sock)
    time.sleep(0.1)
    sock.recv(1024)

    sock.send(exit_input.encode('utf-8'))
    sock.recv(1024)
    time.sleep(1)

    calum_login(sock)
    time.sleep(0.1)

    data = sock.recv(1024).decode('utf-8')
    print(data)
    sock.send(exit_input.encode('utf-8'))
    sock.recv(1024)
    time.sleep(0.1)

    return True if data.startswith('logged') else False


def test_create_user_success():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    create_input = '/create'
    user_input = rand_string()
    pass_input = 'test'

    sock1.send(create_input.encode('utf-8'))
    sock1.recv(1024)
    sock1.send(user_input.encode('utf-8'))
    sock1.recv(1024)
    sock1.send(pass_input.encode('utf-8'))
    sock1.send(pass_input.encode('utf-8'))
    time.sleep(0.1)
    sock1.send("/exit".encode('utf-8'))

    time.sleep(1)

    user_check = db_controller.check_user(user_input)
    print(user_check)
 
    return True if user_check == user_input else False


def test_create_user_fail():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    create_input = '/create'
    user_input = 'calum'

    sock1.send(create_input.encode('utf-8'))
    sock1.recv(1024)
    sock1.send(user_input.encode('utf-8'))
    data = sock1.recv(1024).decode('utf-8')

    return True if data == 'error' else False


def test_delete_user():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    login_input = '/login'
    user_input = db_controller.get_last_user()
    pass_input = 'test'
    delete = '/delete'

    sock1.send(login_input.encode('utf-8'))
    time.sleep(0.1)
    sock1.send(user_input.encode('utf-8'))
    sock1.recv(1024)
    time.sleep(0.1)
    sock1.send(pass_input.encode('utf-8'))
    sock1.recv(1024)
    time.sleep(0.1)
    sock1.send(delete.encode('utf-8'))
    time.sleep(0.1)
    sock1.recv(1024)

    del_input = 'y'
    sock1.send(del_input.encode('utf-8'))

    time.sleep(0.5)

    user_check = db_controller.check_user(user_input)
    print(user_check)

    return True if user_check == "p" else False


def test_send_and_receive_message():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('192.168.56.1', 5000))

    calum_login(sock1)
    joe_login(sock2)

    time.sleep(1)
    sock2.recv(1024)
    message = "hello world"
    sock1.send(message.encode('utf-8'))
    time.sleep(0.1)
    data = sock2.recv(1024).decode('utf-8')
    print(data)

    sock1.send("/exit".encode('utf-8'))
    sock1.recv(1024)
    sock2.send("/exit".encode('utf-8'))
    sock2.recv(1024)
    sock1.close()
    sock2.close()

    return True if data == 'calum (' + ctime()[11:16] + "): hello world \n" else False


def test_direct_messages():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('192.168.56.1', 5000))

    calum_login(sock1)
    joe_login(sock2)

    time.sleep(0.5)
    sock2.recv(1024)
    time.sleep(1)

    message = "hello joe"
    dm = '/dm joe'
    sock1.send(dm.encode('utf-8'))
    time.sleep(0.1)
    sock1.send(message.encode('utf-8'))
    time.sleep(0.1)
    data = sock2.recv(1024).decode('utf-8')
    print(data)

    time.sleep(0.1)

    sock1.send("/exit".encode('utf-8'))
    sock1.recv(1024)
    sock2.send("/exit".encode('utf-8'))
    sock2.recv(1024)
    sock1.close()
    sock2.close()

    return True if data == ('(PM) calum says: ' + message) else False


def test_offline_direct_messages():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    calum_login(sock1)

    time.sleep(0.5)

    message = "hello joe"
    dm = '/dm joe'
    sock1.send(dm.encode('utf-8'))
    time.sleep(0.1)
    sock1.send(message.encode('utf-8'))
    time.sleep(0.1)

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('192.168.56.1', 5000))

    joe_login(sock2)
    time.sleep(0.5)
    data = sock2.recv(1024).decode('utf-8')
    result = data.splitlines()[-1]
    print(result)

    sock1.send("/exit".encode('utf-8'))
    sock1.recv(1024)
    sock2.send("/exit".encode('utf-8'))
    sock2.recv(1024)
    sock1.close()
    sock2.close()

    return True if result == 'calum (' + ctime()[:16] + '): ' + message + ' ' else False


def test_recent_messages():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.56.1', 5000))

    calum_login(sock)

    time.sleep(0.5)

    data = sock.recv(1024).decode('utf-8')
    recent = []
    recent.append('Recent messages: \n')

    messages = db_controller.get_last_six_server_message()

    for mid, name, timestamp, message in messages:
        recent.append("{0} ({1}): {2} \n".format(name, timestamp, message))

    test = data.splitlines(True)[1:8]
    print(test)
    print(recent)

    sock.send("/exit".encode('utf-8'))
    sock.recv(1024)
    sock.close()

    return True if test == recent else False


def test_check_online_users():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    online_input = '/online'

    calum_login(sock1)
    time.sleep(0.5)
    sock1.recv(1024)

    sock1.send(online_input.encode('utf-8'))
    data1 = sock1.recv(1024).decode('utf-8')

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('192.168.56.1', 5000))

    joe_login(sock2)

    time.sleep(0.5)
    sock1.recv(1024)

    sock1.send(online_input.encode('utf-8'))
    data2 = sock1.recv(1024).decode('utf-8')

    print(data1)
    print(data2)

    sock1.send("/exit".encode('utf-8'))
    sock1.recv(1024)
    sock2.send("/exit".encode('utf-8'))
    sock2.recv(1024)
    sock1.close()
    sock2.close()

    check1 = "/online calum, "
    check2 = "/online calum, joe, "

    return True if data1 == check1 and data2 == check2 else False


def test_friend_online_message():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    calum_login(sock1)
    time.sleep(0.5)
    sock1.recv(1024)

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('192.168.56.1', 5000))

    joe_login(sock2)

    data = sock1.recv(1024).decode('utf-8')
    print(data)

    sock1.send("/exit".encode('utf-8'))
    sock1.recv(1024)
    sock2.send("/exit".encode('utf-8'))
    sock2.recv(1024)
    sock1.close()
    sock2.close()

    return True if data.startswith("Your friend joe has joined the server!") else False


def test_add_friend():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('192.168.56.1', 5000))

    create_input = '/create'
    user_input = rand_string()
    pass_input = 'test'

    sock2.send(create_input.encode('utf-8'))
    sock2.recv(1024)
    sock2.send(user_input.encode('utf-8'))
    sock2.recv(1024)
    sock2.send(pass_input.encode('utf-8'))
    sock2.send(pass_input.encode('utf-8'))
    sock2.send("/exit".encode('utf-8'))

    calum_login(sock1)
    time.sleep(0.1)
    sock1.recv(1024)

    add_input = '/add ' + user_input
    sock1.send(add_input.encode('utf-8'))

    time.sleep(0.1)

    result = db_controller.check_if_friend("calum", user_input)
    print(result)

    sock1.send("/exit".encode('utf-8'))
    sock1.recv(1024)
    sock1.close()

    return True if result == "calum" else False


def test_remove_friend():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    calum_friends = db_controller.show_all_friends("calum")

    calum_login(sock1)
    time.sleep(0.1)
    sock1.recv(1024)

    random_friend = random.choice(calum_friends)
    while (random == "joe"):
        random_friend = random.choice(calum_friends)

    delete_message = '/remove ' + random_friend
    sock1.send(delete_message.encode('utf-8'))

    time.sleep(0.5)

    result = db_controller.check_if_friend("calum", random_friend)

    sock1.send("/exit".encode('utf-8'))
    sock1.recv(1024)
    sock1.close()

    return True if result == "pass" else False


def test_check_friends():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(('192.168.56.1', 5000))

    friend_input = '/friends'

    calum_login(sock1)
    time.sleep(0.5)
    sock1.recv(1024)

    sock1.send(friend_input.encode('utf-8'))
    data = sock1.recv(1024).decode('utf-8')
    print(data)

    sock1.send("/exit".encode('utf-8'))
    sock1.recv(1024)
    sock1.close()

    return True if data.startswith("/friends") else False
