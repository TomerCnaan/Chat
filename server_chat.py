import socket
import select
import datetime
import time

#***SOCKET*****
IP = '0.0.0.0'
PORT = 34600
MAX_PARALLEL_CLIENTS = 5

TIMEOUT = 0.005
#**************

#***COMMANDS***
INITIATE_USERNAME = '00'
CHAT_MESSAGE = '01'
ADD_ADMIN = '02'
KICK_USER = '03'
MUTE_USER = '04'
UNMUTE_USER = '05'
PRIVATE_CHAT = '06'
STATS = '07'
#**************

#***GLOBAL VARIABLES***
all_usernames = []  # [username]
clients_dict = {}  # {username : socket}
data_to_handle = []  # [(socket, data)]
admin_list = []  # [socket]
muted_dict = {}  # {username: end of mute}
stats_list = []  # [[username, entrance time, exit time/current time, time delta]]
#**********************

#****MESSAGES****
PROMOTED_MESSAGE = "**You have been promoted to admin!**"
ALREADY_ADMIN = "**The user is already admin**"
NO_PERMISSION = "**You don't have permission to use this command. To use this command you must be admin**"
USERNAME_NOT_EXIST = "**The username you entered doesn't exist**"
MUTED = "**You are currently muted. Your message could not be sent**"
#****************

print 'Server is ready! \n'


def int_to_3bytes_string(num):
    """
    gets an integer. returns 3 bytes string represents the number value
    """
    if num > 99:
        return str(num)
    elif num > 9:
        return '0' + str(num)
    else:
        return '00' + str(num)


def update_stats(_user, _time):
    """
    updates exit time and calculates time delta
    """
    count = 0
    for client_list in stats_list:  # update exit time in stats list
        if _user == client_list[0]:
            stats_list[count][2] = _time

            s_time = client_list[1]
            s_time = datetime.datetime.strptime(s_time, '%H:%M')

            e_time = client_list[2]
            e_time = datetime.datetime.strptime(e_time, '%H:%M')

            stats_list[count][3] = e_time - s_time
            break
        count += 1


def send_message_specific_client(_socket, msg):
    """
    The function sends a string following the protocol rules to a given client.
    """
    _socket.send(int_to_3bytes_string(len(msg)) + msg)
    print 'message sent: ' + int_to_3bytes_string(len(msg)) + msg + '\n'


def send_message_to_all_clients(clients_to_send_to, cl_socket, msg):
    """
    The function sends a given message to all the clients except the client who wrote the message

    arguments:
        clients_to_send_to - contains all the client sockets that are writable
        cl_socket - the socket of the client who wrote the message
    """
    msg = int_to_3bytes_string(len(msg)) + msg
    if cl_socket in clients_to_send_to:
        for client in clients_to_send_to:
            if client in clients_dict.values():
                if client != cl_socket:
                    client.send(msg)
                    print 'message sent \n'


def analyze_data(data):
    """
    The function receives the string from the client. extracts and returns the user name, the command, and also return
    the original string of the command parameters, by following the protocol rules to string structure from client.

    arguments:
        data: the string from the client.
    """

    #extract username
    length_username = int(data[:2:])  # username length is represented with 2 bytes
    _username = data[2:2+length_username:]

    #extract command
    _command = data[2+length_username:4+length_username:]  # command  is represented with 2 bytes

    #parameters string
    if not _command == STATS:
        _params_string = data[4+length_username::]
    else:
        _params_string = None

    return _username, _command, _params_string


def handle_waiting_data(write_list, open_client_sockets):
    """
    arguments:
        write_list: contains all the sockets that are writable
    """
    for _data in data_to_handle:
        (client_socket, data) = _data

        cur_username, cur_command, params_not_analyzed = analyze_data(data)
        cur_time = datetime.datetime.now().time().strftime("%H:%M")

        if cur_command == INITIATE_USERNAME:
            if not cur_username in all_usernames:  # if new client, add to the clients dictionary
                all_usernames.append(cur_username)
                clients_dict[cur_username] = client_socket
                send_message_specific_client(client_socket, "valid")
                stats_list.append([cur_username, cur_time, cur_time, 0])
                if client_socket in admin_list:
                    client_socket.send(int_to_3bytes_string(len(PROMOTED_MESSAGE)) + PROMOTED_MESSAGE)
            else:
                send_message_specific_client(client_socket, "invalid")

        if client_socket in admin_list:
            cur_username = "@" + cur_username

        #-------------------------------------------------------------
        if cur_command == CHAT_MESSAGE:
            is_muted = False
            if cur_username in muted_dict:
                time_now = time.strftime("%H:%M:%S")
                hour, minute, second = time_now.split(":")
                time_now = datetime.timedelta(hours=int(hour), minutes=int(minute), seconds=int(second))
                if muted_dict[cur_username] > time_now:
                    is_muted = True
                    send_message_specific_client(client_socket, MUTED)
                else:
                    muted_dict.pop(cur_username)
            if not is_muted:
                length_msg = int(params_not_analyzed[:3:])  # message length is represented with 3 bytes
                if params_not_analyzed[3:3+length_msg:].lower() == "quit":  # if message is "quit"
                    if cur_username[0] == '@':
                        cur_username = cur_username[1::]
                    update_stats(cur_username, cur_time)
                    msg = cur_time + " You left the chat!"
                    send_message_specific_client(client_socket, msg)
                    clients_dict.pop(cur_username)
                    open_client_sockets.remove(client_socket)
                    msg = cur_time + " " + cur_username + " has left the chat!"
                    send_message_to_all_clients(write_list, client_socket, msg)
                    print "Connection with client closed."
                else:
                    if params_not_analyzed[3:3+length_msg:].lower() == "view-managers":  # if message is "view-managers"
                        msg = cur_time + " admins: "
                        count = 0
                        for user, sock in clients_dict.items():
                            if sock in admin_list:
                                if not count == 0:
                                    msg += ", " + user
                                else:
                                    msg += user
                                    count += 1
                        send_message_specific_client(client_socket, msg)
                    else:
                        msg = cur_time + " " + cur_username + ": " + params_not_analyzed[3:3+length_msg:]
                        send_message_to_all_clients(write_list, client_socket, msg)

        #- - - - - - - - - - - - - - -

        elif cur_command == ADD_ADMIN:
            if client_socket in admin_list:
                length_username_to_add = int(params_not_analyzed[:2:])  # length admin username represented with 2 bytes
                username_to_add = params_not_analyzed[2:2+length_username_to_add:]
                if username_to_add in clients_dict:
                    socket_to_add = clients_dict[username_to_add]
                    if socket_to_add in admin_list:  # if the client is already an admin
                        send_message_specific_client(client_socket, ALREADY_ADMIN)
                    else:
                        admin_list.append(socket_to_add)
                        send_message_specific_client(socket_to_add, PROMOTED_MESSAGE)
                        send_message_specific_client(client_socket, "**" + username_to_add + " promoted to admin successfully**")
                else:
                    send_message_specific_client(client_socket, USERNAME_NOT_EXIST)
            else:
                send_message_specific_client(client_socket, NO_PERMISSION)

        #- - - - - - - - - - - - - - -

        elif cur_command == KICK_USER:
            if client_socket in admin_list:
                length_username_to_kick = int(params_not_analyzed[:2:])  # length username to kick represented with 2 bytes
                username_to_kick = params_not_analyzed[2:2+length_username_to_kick:]
                if username_to_kick in clients_dict:
                    socket_to_kick = clients_dict[username_to_kick]
                    if not socket_to_kick in admin_list:
                        send_message_specific_client(socket_to_kick, "**You have been kicked from the chat!**")
                        update_stats(cur_username, cur_time)
                        open_client_sockets.remove(socket_to_kick)
                        clients_dict.pop(username_to_kick)
                        msg = cur_time + " **" + username_to_kick + " has been kicked from the chat!**"
                        send_message_to_all_clients(write_list, socket_to_kick, msg)
                    else:
                        send_message_specific_client(client_socket, "**You do not have a permission to kick other admins**")
                else:
                    send_message_specific_client(client_socket, USERNAME_NOT_EXIST)
            else:
                send_message_specific_client(client_socket, NO_PERMISSION)

        #- - - - - - - - - - - - - - -

        elif cur_command == MUTE_USER:
            if client_socket in admin_list:
                length_username_to_mute = int(params_not_analyzed[:2:])  # length username to mute represented with 2 bytes
                username_to_mute = params_not_analyzed[2:2+length_username_to_mute:]
                if username_to_mute in clients_dict:
                    if not clients_dict[username_to_mute] in admin_list:  # if user to mute is not admin
                        time_to_mute = int(params_not_analyzed[2+length_username_to_mute::])
                        cur_time = time.strftime("%H:%M:%S")
                        hour, minute, second = cur_time.split(":")
                        expired_time = datetime.timedelta(minutes=time_to_mute) + datetime.timedelta(hours=int(hour), minutes=int(minute),
                                                                                                     seconds=int(second))
                        muted_dict[username_to_mute] = expired_time
                        msg = cur_time + " **" + username_to_mute + " has been muted for " + str(time_to_mute) + " minutes**"
                        send_message_to_all_clients(write_list, clients_dict[username_to_mute], msg)
                        msg = cur_time + " **You have been muted for " + str(time_to_mute) + " minutes**"
                        send_message_specific_client(clients_dict[username_to_mute], msg)
                    else:
                        send_message_specific_client(client_socket, "**You do not have a permission to mute other admins**")
                else:
                    send_message_specific_client(client_socket, USERNAME_NOT_EXIST)
            else:
                send_message_specific_client(client_socket, NO_PERMISSION)

        #- - - - - - - - - - - - - - -

        elif cur_command == UNMUTE_USER:
            if client_socket in admin_list:
                length_username_to_unmute = int(params_not_analyzed[:2:])  # length username to mute represented with 2 bytes
                username_to_unmute = params_not_analyzed[2:2+length_username_to_unmute:]
                if clients_dict[cur_username] in admin_list:
                    if username_to_unmute in clients_dict:
                        if username_to_unmute in muted_dict:
                            muted_dict.pop(username_to_unmute)
                            send_message_specific_client(clients_dict[username_to_unmute], "**Your mute has been removed**")
                            send_message_specific_client(client_socket, "**The mute has been removed successfully**")
                        else:
                            send_message_specific_client(client_socket, "**" + username_to_unmute + " is not muted**")
                    else:
                        send_message_specific_client(client_socket, USERNAME_NOT_EXIST)
                else:
                    send_message_specific_client(client_socket, NO_PERMISSION)

        #- - - - - - - - - - - - - - -

        elif cur_command == STATS:
            count = 0
            for client_list in stats_list:  # update exit time in stats list
                temp = client_list[0]
                if client_list[0] == '@':  # if username starts with @
                    temp = client_list[0][1::]
                    print "i know its an admin"
                if temp in clients_dict.keys():
                    stats_list[count][2] = cur_time

                    s_time = client_list[1]
                    s_time = datetime.datetime.strptime(s_time, '%H:%M')

                    e_time = client_list[2]
                    e_time = datetime.datetime.strptime(e_time, '%H:%M')

                    stats_list[count][3] = e_time - s_time
                count += 1
            print stats_list
            stats_list.sort(key=lambda element: element[3], reverse=True)

            if cur_username[0] == '@':
                cur_username = cur_username[1::]
            msg = cur_time + " **Stats:"
            send_message_specific_client(clients_dict[cur_username], msg)
            exit_or_current_time = ""
            for index in range(len(stats_list)):
                if stats_list[index][0] in clients_dict.keys():
                    exit_or_current_time = "Current time(still online): "
                else:
                    exit_or_current_time = "Exit time: "
                msg = "           " + stats_list[index][0] + ":    Entrance time: " + stats_list[index][1] + "    " + exit_or_current_time + \
                      stats_list[index][2]
                send_message_specific_client(clients_dict[cur_username], msg)

        #- - - - - - - - - - - - - - -

        elif cur_command == PRIVATE_CHAT:
            is_muted = False
            if cur_username in muted_dict:
                time_now = time.strftime("%H:%M:%S")
                hour, minute, second = time_now.split(":")
                time_now = datetime.timedelta(hours=int(hour), minutes=int(minute), seconds=int(second))
                if muted_dict[cur_username] > time_now:
                    is_muted = True
                    send_message_specific_client(client_socket, MUTED)
                else:
                    muted_dict.pop(cur_username)
            if not is_muted:
                length_username_to_direct = int(params_not_analyzed[:2:])  # length username to direct msg represented with 2 bytes
                username_to_direct = params_not_analyzed[2:2+length_username_to_direct:]
                if username_to_direct in clients_dict:
                    length_msg = int(params_not_analyzed[2+length_username_to_direct:2+length_username_to_direct+3:])
                    msg = cur_time + " !" + cur_username + ": " + params_not_analyzed[2+length_username_to_direct+3:
                                                                                      2+length_username_to_direct+3 + length_msg:]
                    send_message_specific_client(clients_dict[username_to_direct], msg)
                else:
                    send_message_specific_client(client_socket, USERNAME_NOT_EXIST)
        #----------------------------------------------------------

    del data_to_handle[:]


def main():

    server_socket = socket.socket()
    server_socket.bind((IP, PORT))
    server_socket.listen(MAX_PARALLEL_CLIENTS)
    open_client_sockets = []

    while True:
        read_list, write_list, error_list = select.select([server_socket] + open_client_sockets,  open_client_sockets, [], TIMEOUT)
        # rList contains everyone
        # wList contains only those with an active socket
        # xList - unused

        global admin_list

        for current_socket in read_list:
            if current_socket is server_socket:
                (new_socket, address) = server_socket.accept()
                print 'new connection'
                if not open_client_sockets:
                    admin_list.append(new_socket)
                open_client_sockets.append(new_socket)
            else:
                try:
                    data = current_socket.recv(1024)
                except Exception as ex:
                    open_client_sockets.remove(current_socket)
                    print "Connection with client closed."
                    continue

                # if the client sends a message saying ""quit" the server removes the client
                if data == "":
                    cur_time = datetime.datetime.now().time().strftime("%H:%M")
                    msg = cur_time + " **"
                    cur_user = ""
                    for user, sock in clients_dict.items():
                        if sock == current_socket:
                            clients_dict.pop(user)
                            msg += user
                            cur_user = user
                    if not cur_user is None:
                        msg += " has left the chat**"
                        update_stats(cur_user, cur_time)
                        send_message_to_all_clients(write_list, current_socket, msg)
                    open_client_sockets.remove(current_socket)

                    print "Connection with client closed."
                else:
                    print 'Client data: ', data, '\n'
                    data_to_handle.append((current_socket, data))

        for admin in admin_list:
            if not admin in open_client_sockets:
                admin_list.remove(admin)
        handle_waiting_data(write_list, open_client_sockets)


if __name__ == '__main__':
    main()