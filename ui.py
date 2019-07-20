from Tkinter import *

root = Tk()
root.wm_geometry("470x400")
root.title("CHAT")
my_msg = StringVar()  # For the messages to be sent

scrollbar = Scrollbar(root)  # To navigate through past messages
msg_list = Listbox(root, height=22, width=65, yscrollcommand=scrollbar.set)  # where the chat messages are shown
my_msg.set("Type your messages here.")
scrollbar.pack(side=RIGHT, fill=Y)
msg_list.pack(side=TOP, fill=BOTH, expand=True)

bottom_frame = Frame(root)
bottom_frame.pack(side=BOTTOM, fill=BOTH, expand=True)

entry_field = Entry(bottom_frame, textvariable=my_msg, width=50, justify=CENTER)  # where the client writes
entry_field.bind("<Return>", lambda event=None, cl_socket=my_socket: send(event, cl_socket))
entry_field.pack(side=LEFT, fill=BOTH, expand=True)
send_button = Button(bottom_frame, fg="dark green", font=("Helvetica", 10, "bold italic"), text="send",
                     command=lambda event=None, cl_socket=my_socket: send(event, cl_socket))
send_button.pack(side=LEFT, fill=BOTH, expand=True)
clear_button = Button(bottom_frame, fg="SteelBlue2", font=("Helvetica", 10, "bold italic"), text="clear screen",
                      command=lambda event=None, text_list=msg_list: clear(event, text_list))
clear_button.pack(side=RIGHT, fill=BOTH, expand=True)

root.mainloop()