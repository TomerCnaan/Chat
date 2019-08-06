import socket
import select
import datetime

#***SOCKET*****
IP = '0.0.0.0'
PORT = 34600
MAX_PARALLEL_CLIENTS = 5

TIMEOUT = 0.005
#**************

#***COMMANDS***
CHAT_MESSAGE = '01'
ADD_ADMIN = '02'
KICK_USER = '03'
MUTE_USER = '04'
UNMUTE_USER = '05'
PRIVATE_CHAT = '06'
#**************

#***GLOBAL VARIABLES***
clients_dict = {}  # {username : socket}
data_to_handle = []  # [(socket, data)]
admin_list = []  # [socket]
#**********************

#****MESSAGES****
PROMOTED_MESSAGE = "**You have been promoted to admin!**"
ALREADY_ADMIN = "**The user is already admin**"
NO_PERMISSION = "**You don't have permission to use this command. To use this command you must be admin**"
USERNAME_NOT_EXIST = "**The username you entered doesn't exist**"
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


def send_message_specific_client(_socket, msg):
    """
    The function sends a string following the protocol rules to a given client.
    """
    _socket.send(int_to_3bytes_string(len(msg)) + msg)


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
    _params_string = data[4+length_username::]

    return _username, _command, _params_string


def handle_waiting_data(write_list, open_client_sockets):
    """
    arguments:
        write_list: contains all the sockets that are writable
    """
    for _data in data_to_handle:
        (client_socket, data) = _data

        cur_username, cur_command, params_not_analyzed = analyze_data(data)
        if not cur_username in clients_dict:  # if new client, add to the clients dictionary
            clients_dict[cur_username] = client_socket

        if client_socket in admin_list:
            cur_username = "@" + cur_username
        cur_time = datetime.datetime.now().time().strftime("%H:%M")
        #-------------------------------------------------------------
        if cur_command == CHAT_MESSAGE:
            length_msg = int(params_not_analyzed[:3:])  # message length is represented with 3 bytes
            if params_not_analyzed[3:3+length_msg:].lower() == "quit":  # if message is "quit"
                open_client_sockets.remove(client_socket)
                clients_dict.pop(cur_username)
                msg = cur_time + " " + cur_username + " has left the chat!"
                send_message_to_all_clients(write_list, client_socket, msg)
                print "Connection with client closed."
            msg = cur_time + " " + cur_username + ": " + params_not_analyzed[3:3+length_msg:]
            send_message_to_all_clients(write_list, client_socket, msg)

        #- - - - - - - - - - - - - - -

        if cur_command == ADD_ADMIN:
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
                else:
                    send_message_specific_client(client_socket, USERNAME_NOT_EXIST)
            else:
                send_message_specific_client(client_socket, NO_PERMISSION)

        #- - - - - - - - - - - - - - -

        if cur_command == KICK_USER:
            if client_socket in admin_list:
                length_username_to_kick = int(params_not_analyzed[:2:])  # length username to kick represented with 2 bytes
                username_to_kick = params_not_analyzed[2:2+length_username_to_kick:]
                socket_to_kick = clients_dict[username_to_kick]
                if not socket_to_kick in admin_list:
                    if username_to_kick in clients_dict:
                        send_message_specific_client(socket_to_kick, "You have been kicked from the chat!")
                        open_client_sockets.remove(socket_to_kick)
                        clients_dict.pop(username_to_kick)
                        msg = cur_time + " " + username_to_kick + " has been kicked from the chat!"
                        send_message_to_all_clients(write_list, socket_to_kick, msg)
                    else:
                        send_message_specific_client(client_socket, USERNAME_NOT_EXIST)
                else:
                    send_message_specific_client(client_socket, NO_PERMISSION)
            else:
                send_message_specific_client(client_socket, NO_PERMISSION)
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

        for current_socket in read_list:
            if current_socket is server_socket:
                (new_socket, address) = server_socket.accept()
                if not open_client_sockets:
                    admin_list.append(new_socket)
                    new_socket.send(int_to_3bytes_string(len(PROMOTED_MESSAGE)) + PROMOTED_MESSAGE)
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
                    open_client_sockets.remove(current_socket)
                    print "Connection with client closed."
                else:
                    print 'Client data: ', data, '\n'
                    data_to_handle.append((current_socket, data))
        handle_waiting_data(write_list, open_client_sockets)


if __name__ == '__main__':
    main()