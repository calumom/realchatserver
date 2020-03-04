import db_controller

BUFFER_SIZE = 8192

# TODO: change to OO


class UserClient:

    def __init__(self, username, identifier, password, friends):
        self.username = username
        self.identifier = identifier
        self.password = password
        self.friends = friends

    
    def add_friend(self, target_friend):

        friend_check = db_controller.check_user(target_friend)

        if friend_check == target_friend:
            result = db_controller.check_if_friend(self.username, target_friend)
        
            if result == 'pass':
                db_controller.add_friend_to_db(self.username, target_friend)

                message = "/success"

            else:
                message = "/alreadyexists"
        
        else:
            message = "/nouser"

        return message


    def remove_friend(self, target_remove):

        user_check = db_controller.check_user(target_remove)

        if user_check == target_remove:
            friend_check = db_controller.check_if_friend(self.username, target_remove)

            if friend_check == self.username:
                db_controller.remove_friend_from_db(self.username, target_remove)

                message = "{0} has been removed from your friend list\n".format(target_remove)
                 
            else:
                message = "User is not a friend"       

        else:
            message = "User does not exist"

        return message


    def show_online_friends(self, online_users):

        online_friends = []
        offline_friends = []

        for friend in self.friends:
            if friend in online_users:
                online_friends.append(friend)
            else:
                offline_friends.append(friend)

        separator = ', '
        online = separator.join(online_friends)
        offline = separator.join(offline_friends)
                
        message = "Online: {0} \n Offline: {1}".format(online, offline)

        return message
