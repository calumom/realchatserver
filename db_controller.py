import sqlite3
from time import ctime


def create_table(create_table_sql):
    conn = sqlite3.connect(r"users.db")
    c = conn.cursor()
    c.execute(create_table_sql)


def create_user(user):
    conn = sqlite3.connect(r"users.db")

    sql = """ INSERT INTO all_users(name, id, password)
              VALUES(?, ?, ?) """
    
    cursor = conn.cursor()
    cursor.execute(sql, user)
    conn.commit()
    conn.close()


def add_user_to_db(name, user_id, password):
    new_user = (name, user_id, password)
    create_user(new_user)


def check_user(name):
    conn = sqlite3.connect(r"users.db")

    sql = "SELECT name FROM all_users where name = ?"

    cursor = conn.cursor()
    cursor.execute(sql, (name,))
    conn.commit()

    try:
        result = cursor.fetchone()
    except:
        result = "pass"

    if result is None:
        result = "pass"

    conn.close()
    return result[0]


def get_all_users():
    conn = sqlite3.connect(r"users.db")
   
    sql = """ SELECT name FROM all_users """

    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

    result =  cursor.fetchall()
    conn.close()

    return list(map(lambda x: x[0], result))


def return_last_user_id():
    conn = sqlite3.connect(r"users.db")

    sql = "SELECT id FROM all_users ORDER BY id DESC LIMIT 1"

    cursor = conn.cursor()
    cursor.execute(sql)

    result = cursor.fetchone()[0]

    conn.close()
    return result

def get_user_id(name):
    conn = sqlite3.connect(r"users.db")

    sql = "SELECT id FROM  all_users WHERE name = ?"

    cursor = conn.cursor()
    cursor.execute(sql, (name,))

    result = cursor.fetchone()[0]

    conn.close()
    return result

def return_password(name):
    conn = sqlite3.connect(r"users.db")

    sql = "SELECT password FROM all_users WHERE name=?"

    cursor = conn.cursor()
    cursor.execute(sql, (name,))

    password = cursor.fetchone()[0]

    conn.close()
    return password


def delete_user(name):
    conn = sqlite3.connect(r"users.db")

    sql = """ DELETE FROM all_users WHERE name=? """

    cursor = conn.cursor()
    cursor.execute(sql, (name,))
    conn.commit()
    conn.close()


def delete_user_from_db(name):
    delete_user(name)


def delete_user_from_friends_list(name):
    conn = sqlite3.connect(r"users.db")

    sql = """ DELETE FROM friends WHERE name = ? OR friend = ? """

    cursor = conn.cursor()
    cursor.execute(sql, name)
    conn.commit()
    conn.close()


def delete_user_from_friend_db(name):
    user_delete = (name, name)
    delete_user_from_friends_list(user_delete)


def add_friend(user):
    conn = sqlite3.connect(r"users.db")

    sql = """INSERT INTO friends(name, friend)
                VALUES(?, ?) """
    
    cursor = conn.cursor()
    cursor.execute(sql, user)
    conn.commit()
    conn.close()


def add_friend_to_db(name, target):
    add = (name, target)
    add_friend(add)


def remove_friend(user):
    conn = sqlite3.connect(r"users.db")

    sql = """ DELETE FROM friends WHERE name = ? AND friend = ? """

    cursor = conn.cursor()
    cursor.execute(sql, user)
    conn.commit()
    conn.close()


def remove_friend_from_db(name, target):
    remove = (name, target)
    remove_friend(remove)


def check_if_friend(user, friend):
    conn = sqlite3.connect(r"users.db")

    sql = """ SELECT name FROM friends WHERE name = ? AND friend = ? """
    cursor = conn.cursor()
    cursor.execute(sql, (user, friend))
    conn.commit()

    try:
        result = cursor.fetchone()
    except:
        result = "pass"

    if result is None:
        result = "pass"

    conn.close()
    return result[0]


def show_all_friends(user):
    conn = sqlite3.connect(r"users.db")

    sql = """ SELECT friend FROM friends WHERE name = ? """
    cursor = conn.cursor()
    cursor.execute(sql, (user,))
    conn.commit()

    result =  cursor.fetchall()
    conn.close()

    return list(map(lambda x: x[0], result))


def get_user_added(user):
    conn = sqlite3.connect(r"users.db")

    sql = """ SELECT name FROM friends WHERE friend = ? """
    cursor = conn.cursor()
    cursor.execute(sql, (user,))
    conn.commit()

    result =  cursor.fetchall()
    conn.close()

    return list(map(lambda x: x[0], result))


def save_server_message(message):
    conn = sqlite3.connect(r"users.db")

    sql = """ INSERT INTO server_messages(name, timestamp, message)
                VALUES(?, ?, ?) """

    cursor = conn.cursor()
    cursor.execute(sql, message)
    conn.commit()
    conn.close()


def save_server_message_to_db(username, message):
    save_message = (username, ctime()[:16], message)

    save_server_message(save_message)


def get_last_six_server_message():
    conn = sqlite3.connect(r"users.db")

    sql = "SELECT * FROM server_messages ORDER BY id DESC LIMIT 6"

    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

    result = cursor.fetchall()
    conn.close()

    return result


def save_direct_message(message):
    conn = sqlite3.connect(r"users.db")
   
    sql = """ INSERT INTO direct_messages(name, timestamp, message, recipient)
                VALUES(?, ?, ?, ?) """

    cursor = conn.cursor()
    cursor.execute(sql, message)
    conn.commit()
    conn.close()


def save_direct_message_to_db(username, message, recipient):
    save_message = (username, ctime()[:16], message, recipient)

    save_direct_message(save_message)


def get_direct_messages(user):
    conn = sqlite3.connect(r"users.db")

    sql = """ SELECT * FROM direct_messages WHERE recipient = ? """

    cursor = conn.cursor()
    cursor.execute(sql, (user,))
    conn.commit()
    result = cursor.fetchall()

    conn.close()
    return result


def delete_direct_messages(user):
    conn = sqlite3.connect(r"users.db")

    sql = """ DELETE FROM direct_messages WHERE recipient = ? """

    cursor = conn.cursor()
    cursor.execute(sql, (user,))
    conn.commit()
    conn.close()


def get_last_user():
    conn = sqlite3.connect(r"users.db")

    sql = "SELECT name FROM all_users ORDER BY id DESC LIMIT 1"

    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

    result = cursor.fetchone()[0]
    conn.close()

    return result


def main():
    conn = sqlite3.connect(r"users.db")
    
    sql = """ """
    
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()


if __name__ == '__main__':
    main()
