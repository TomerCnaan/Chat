import socket
import select
import re
import sys
import datetime
import time
from Tkinter import *
from login_gui import *

#***SOCKET***
IP = '127.0.0.1'
PORT = 34600

TIMEOUT = 0.005
#************

#**GUI**
FONT1 = "-family {Open Sans} -size 20 -weight bold -slant "  \
        "roman -underline 0 -overstrike 0"
FONT1_SMALL = "-family {Open Sans} -size 11 -weight normal -slant "  \
        "roman -underline 0 -overstrike 0"
FONT1_MEDIUM = "-family {Open Sans} -size 14 -weight normal -slant "  \
        "roman -underline 0 -overstrike 0"
FONT1_TINY = "-family {Open Sans} -size 10 -weight normal -slant "  \
        "roman -underline 0 -overstrike 0"

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
DEFAULT_MUTE_TIME = '03'
INVALID_INPUT = '**System alert: Your input is not valid. Make sure you follow the chat protocol**'

print 'Client is ready! \n'

#**USERNAME**
username = ''
#************
validation = False


def check_username(event, cl_socket, toplevel):
    """
    handles username validation
    """
    global validation

    if re.match("^[a-zA-Z0-9_.-]{3,12}$", username.get()):
        is_exist_query = int_to_2bytes_string(len(username.get())) + username.get() + INITIATE_USERNAME
        cl_socket.send(is_exist_query)
        length_server_data = int(cl_socket.recv(3))  # receive the length of the server data(always 3 bytes string)
        server_data = cl_socket.recv(length_server_data)
        print server_data
        if server_data == "valid":
            validation = True
            toplevel.destroy()
            print 'valid username'
        elif server_data == "invalid":
            print 'invalid username'
            msg_invalid.set("UserName is already taken! peek a different name")
    elif len(username.get()) < 3 or len(username.get()) > 12:
        msg_invalid.set("Username length is between 3 to 12")
    elif " " in username.get():
        msg_invalid.set("Spaces are not allowed!")
    else:
        msg_invalid.set("The allowed symbols are:  _.-")


def login_page(sock):
    """
    gui and functionality of the login page
    """
    root = Tk()

    root.geometry("360x349+786+200")
    root.title("Login")
    root.configure(background="#444")
    root.configure(highlightbackground="#d9d9d9")
    root.configure(highlightcolor="black")

    global username
    username = StringVar()
    username.set("username")

    global msg_invalid
    msg_invalid = StringVar()

    login_frame = Frame(root)
    login_frame.place(relx=0.0, rely=-0.029, relheight=1.046, relwidth=1.014)
    login_frame.configure(borderwidth="1")
    login_frame.configure(background="#444")
    login_frame.configure(width=365)

    welcome_label = Label(login_frame)
    welcome_label.place(relx=0.0, rely=0.11, height=81, width=354)
    welcome_label.configure(background="#444")
    welcome_label.configure(font=FONT1)
    welcome_label.configure(foreground="white")
    welcome_label.configure(text='''Welcome to the chat!''')

    enter_label = Label(login_frame)
    enter_label.place(relx=0.205, rely=0.301, height=31, width=194)
    enter_label.configure(background="#444")
    enter_label.configure(font=FONT1_MEDIUM)
    enter_label.configure(foreground="white")
    enter_label.configure(text='''Enter username''')

    username_entry = Entry(login_frame)
    username_entry.place(relx=0.205, rely=0.411, height=30, relwidth=0.559)
    username_entry.configure(background="white")
    username_entry.configure(font=FONT1_MEDIUM)
    username_entry.configure(foreground="black")
    username_entry.configure(textvariable=username)
    username_entry.bind("<Return>", lambda event=None, cl_socket=sock, toplevel=root: check_username(event, cl_socket, toplevel))

    btn_login = Button(login_frame)
    btn_login.place(relx=0.205, rely=0.575, height=34, width=204)
    btn_login.configure(background="#31e0c9")
    btn_login.configure(font=FONT1_SMALL)
    btn_login.configure(foreground="black")
    btn_login.configure(text='''Login''')
    btn_login.configure(width=197)
    btn_login.configure(command=lambda event=None, cl_socket=sock, toplevel=root: check_username(event, cl_socket, toplevel))

    canvas1 = Canvas(login_frame)
    canvas1.place(relx=0.055, rely=0.795, relheight=0.003, relwidth=0.83)
    canvas1.configure(background="#d9d9d9")
    canvas1.configure(relief="ridge")
    canvas1.configure(width=303)

    info_msg_label = Label(login_frame)
    info_msg_label.place(relx=0.068, rely=0.822, height=51, width=294)
    info_msg_label.configure(background="#444")
    info_msg_label.configure(borderwidth="0")
    info_msg_label.configure(font=FONT1_TINY)
    info_msg_label.configure(foreground="white")
    info_msg_label.configure(justify='left')
    info_msg_label.configure(textvariable=msg_invalid)

    root.mainloop()


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
        show_my_msg = datetime.datetime.now().time().strftime("%H:%M") + " (me)" + username.get() + ": " + msg
        msg_list.insert(END, show_my_msg)

        command_data_to_server = CHAT_MESSAGE + int_to_3bytes_string(len(msg)) + msg
        return command_data_to_server

    else:
        current_command_and_params = msg[2::].split()
        current_command = current_command_and_params[0].lower()

        if current_command == "add_admin":
            if len(current_command_and_params) == 2:
                user_to_promote = current_command_and_params[1]
                command_data_to_server = ADD_ADMIN + int_to_2bytes_string(len(user_to_promote)) + user_to_promote
                return command_data_to_server
            else:
                return INVALID_INPUT

        elif current_command == "kick":
            if len(current_command_and_params) == 2:
                user_to_kick = current_command_and_params[1]
                command_data_to_server = KICK_USER + int_to_2bytes_string(len(user_to_kick)) + user_to_kick
                return command_data_to_server
            else:
                return INVALID_INPUT

        elif current_command == "mute":
            mute_time = ""
            if len(current_command_and_params) == 3:
                user_to_mute = current_command_and_params[1]
                if current_command_and_params[2].isdigit():
                    mute_time = int_to_2bytes_string(int(current_command_and_params[2]))
                else:
                    return INVALID_INPUT
            elif len(current_command_and_params) == 2:
                user_to_mute = current_command_and_params[1]
                mute_time = DEFAULT_MUTE_TIME
            else:
                return INVALID_INPUT
            command_data_to_server = MUTE_USER + int_to_2bytes_string(len(user_to_mute)) + user_to_mute + mute_time
            return command_data_to_server

        elif current_command == "unmute":
            if len(current_command_and_params) == 2:
                user_to_unmute = current_command_and_params[1]
                command_data_to_server = UNMUTE_USER + int_to_2bytes_string(len(user_to_unmute)) + user_to_unmute
                return command_data_to_server
            else:
                return INVALID_INPUT

        elif current_command == "private_msg":
            if len(current_command_and_params) >= 3:
                user_to_direct = current_command_and_params[1]
                del current_command_and_params[0:2]
                direct_msg = " ".join(current_command_and_params)
                show_my_msg = datetime.datetime.now().time().strftime("%H:%M") + " !(me)" + username.get() + ": " + direct_msg
                msg_list.insert(END, show_my_msg)
                command_data_to_server = PRIVATE_CHAT + int_to_2bytes_string(len(user_to_direct)) + user_to_direct +\
                                                                                                int_to_3bytes_string(len(direct_msg)) + direct_msg
                return command_data_to_server
            else:
                return INVALID_INPUT

        elif current_command == "stats":
            return STATS

        else:
            return INVALID_INPUT


def handle_input(event, cl_socket):
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
        msg_list.insert(END, INVALID_INPUT)
        my_msg.set("")
        return None

    data_to_server = int_to_2bytes_string(len(username.get())) + username.get() + command_data
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
    #-----------------

    login_page(my_socket)
    if not validation:
        print "client failed to choose a valid username"
        my_socket.close()
        sys.exit(0)

    #-----------------

    # chat page
    root = Tk()
    root.wm_geometry("500x400")
    root.title("CHAT")
    global my_msg
    my_msg = StringVar()

    frame = Frame(root)
    frame.pack()
    global msg_list
    msg_list = Listbox(frame, width=100, height=23)  # where the chat messages are shown
    scrollbar = Scrollbar(frame, orient="vertical")  # To navigate through past messages
    scrollbar.config(command=msg_list.yview)
    scrollbar.pack(side="right", fill="y")
    msg_list.configure(yscrollcommand=scrollbar.set)
    my_msg.set("Type your messages here.")
    scrollbar.pack(side=RIGHT, fill=Y)
    msg_list.pack(side=TOP, fill=BOTH, expand=True)

    bottom_frame = Frame(root, bg="white")
    bottom_frame.pack(side=BOTTOM, fill=BOTH)

    entry_field = Entry(bottom_frame, textvariable=my_msg, width=50, justify=LEFT)  # where the client writes
    entry_field.bind("<Return>", lambda event=None, cl_socket=my_socket: handle_input(event, cl_socket))
    entry_field.pack(side=LEFT, fill=BOTH)
    send_button = Button(bottom_frame, fg="dark green", font=("Helvetica", 10, "bold italic"), text="send",
                         command=lambda event=None, cl_socket=my_socket: handle_input(event, cl_socket))
    send_button.pack(side=LEFT, fill=BOTH)
    clear_button = Button(bottom_frame, fg="SteelBlue2", font=("Helvetica", 10, "bold italic"), text="clear screen",
                          command=lambda event=None, text_list=msg_list: clear(event, text_list))
    clear_button.pack(side=LEFT, fill=BOTH)
    #****************************

    while True:

        try:

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
        except Exception, e:
            print str(e)
            my_socket.close()
            sys.exit(0)

    my_socket.close()
    sys.exit(0)

if __name__ == '__main__':
    main()
