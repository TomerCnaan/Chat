import socket
import select
import msvcrt
import sys
from Tkinter import *

#***SOCKET***
IP = '127.0.0.1'
PORT = 34600

TIMEOUT = 0.005
#************

#***COMMANDS***
CHAT_MESSAGE = '01'
ADD_ADMIN = '02'
KICK_USER = '03'
MUTE_USER = '04'
UNMUTE_USER = '05'
PRIVATE_CHAT = '06'
#**************
DEFAULT_MUTE_TIME = '03'
INVALID_INPUT = '**System alert: Your input is not valid. Make sure you follow the chat protocol**'

print 'Client is ready! \n'

#******UI*******
root = Tk()
root.wm_geometry("500x400")
root.title("CHAT")
my_msg = StringVar()  # For the messages to be sent
#***************

user_name = raw_input("enter username")


def int_to_2bytes_string(num):
    """
    gets an integer. returns 2 bytes string represents the number value
    """
    if num > 9:
        return str(num)
    else:
        return '0' + str(num)


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


def handle_command(msg):
    """
    The function identifies the command and the command parameters from the user input and returns a string
    of the command and command parameters following the command type and the protocol.
    """
    command_data_to_server = ""
    current_command = ""

    if msg[0:2:1] != ">>":
        command_data_to_server = CHAT_MESSAGE + int_to_3bytes_string(len(msg)) + msg
        return command_data_to_server

    else:
        current_command_and_params = msg[2::].split()
        current_command = current_command_and_params[0].lower()

        if current_command == "add_admin":
            user_to_promote = current_command_and_params[1]
            command_data_to_server = ADD_ADMIN + int_to_2bytes_string(len(user_to_promote)) + user_to_promote
            return command_data_to_server

        elif current_command == "kick":
            user_to_kick = current_command_and_params[1]
            command_data_to_server = KICK_USER + int_to_2bytes_string(len(user_to_kick)) + user_to_kick
            return command_data_to_server

        elif current_command == "mute":
            mute_time = ""
            user_to_mute = current_command_and_params[1]
            if len(current_command_and_params) == 3:
                if current_command_and_params[2].isdigit():
                    mute_time = int_to_2bytes_string(int(current_command_and_params[2]))
                else:
                    return INVALID_INPUT
            elif len(current_command_and_params) == 2:
                mute_time = DEFAULT_MUTE_TIME
            else:
                return INVALID_INPUT
            command_data_to_server = MUTE_USER + int_to_2bytes_string(len(user_to_mute)) + user_to_mute + mute_time
            return command_data_to_server

        elif current_command == "unmute":
            user_to_unmute = current_command_and_params[1]
            command_data_to_server = UNMUTE_USER + int_to_2bytes_string(len(user_to_unmute)) + user_to_unmute
            return command_data_to_server

        else:
            return INVALID_INPUT


def handle_input(event, cl_socket, username):
    """
    Function is called when the user sends his input by clicking ENTER or pressing the 'send' button.
    The function sends a string to the server containing data from the user following the protocol rules:
    string- [length username 2 bytes | username | command 2 bytes | command parameters]
    example: 04John01005hello
    """

    msg = my_msg.get()
    if msg == "":
        return None

    command_data = handle_command(msg)
    if command_data == INVALID_INPUT:
        print INVALID_INPUT
        my_msg.set("")
        return None

    data_to_server = int_to_2bytes_string(len(username)) + username + command_data
    print data_to_server

    my_msg.set("")
    cl_socket.send(data_to_server)


def clear(event, text_list):
    """
    when 'clear' button is pressed this function will be called.
    the function removes all the text from the msg_list
    """
    text_list.delete(0, END)


def main():
   # open socket with the server
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, PORT))
    socket_list = [my_socket]

    #*******User Interface*******

    #initialize username

    #-----------------

    scrollbar = Scrollbar(root)  # To navigate through past messages
    msg_list = Listbox(root, yscrollcommand=scrollbar.set)  # where the chat messages are shown
    my_msg.set("Type your messages here.")
    scrollbar.pack(side=RIGHT, fill=Y)
    msg_list.pack(side=TOP, fill=BOTH, expand=True)

    bottom_frame = Frame(root, bg="Grey65")
    bottom_frame.pack(side=BOTTOM, fill=BOTH)

    entry_field = Entry(bottom_frame, textvariable=my_msg, width=50, justify=LEFT)  # where the client writes
    entry_field.bind("<Return>", lambda event=None, cl_socket=my_socket, username=user_name: handle_input(event, cl_socket
                                                                                                        , username))
    entry_field.pack(side=LEFT, fill=BOTH)
    send_button = Button(bottom_frame, fg="dark green", font=("Helvetica", 10, "bold italic"), text="send",
                         command=lambda event=None, cl_socket=my_socket, username=user_name: handle_input(event, cl_socket
                                                                                                        , username))
    send_button.pack(side=LEFT, fill=BOTH)
    clear_button = Button(bottom_frame, fg="SteelBlue2", font=("Helvetica", 10, "bold italic"), text="clear screen",
                          command=lambda event=None, text_list=msg_list: clear(event, text_list))
    clear_button.pack(side=LEFT, fill=BOTH)
    #****************************

    while True:

        root.update_idletasks()
        root.update()

        #if the server sends data to the client the 'read_list' variable will get the socket with the message
        read_list, write_list, error_list = select.select(socket_list, [], [], TIMEOUT)

        #if there is data from the server the client will read it and print it
        if len(read_list) != 0:
            length_server_data = int(my_socket.recv(3))  # receive the length of the server data(always 3 bytes string)
            server_data = my_socket.recv(length_server_data)
            if server_data is None:
                print None
            else:
                msg_list.insert(END, server_data)

    my_socket.close()

if __name__ == '__main__':
    main()