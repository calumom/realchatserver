import json
import db_controller


def show_recent_messages(client_socket):

    message_to_send = '\nRecent messages: \n'

    recent_messages = db_controller.get_last_six_server_message()
    
    for m_id, name, timestamp, message in recent_messages:
        message_to_send += "{0} ({1}): {2} \n".format(name, timestamp, message)

    return message_to_send


def show_direct_messages(client_socket, username):

    message_to_send = ' \nDMs received while offline: \n\n'

    recent_messages = db_controller.get_direct_messages(username)

    for name, timestamp, message, recipient in recent_messages:
        message_to_send += "{0} ({1}): {2} \n".format(name, timestamp, message)

    db_controller.delete_direct_messages(username)
    return message_to_send