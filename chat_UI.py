from Tkinter import *

'''#creating a blank window
root = Tk()

top_frame = Frame(root)
top_frame.pack(side=TOP)
bottom_frame = Frame(root)
bottom_frame.pack(side=BOTTOM)

button1 = Button(top_frame, text="Button 1", fg="red")
button2 = Button(top_frame, text="Button 2", fg="blue")
button3 = Button(top_frame, text="Button 3", fg="green")
button4 = Button(bottom_frame, text="Button 4", fg="purple")

button1.pack(side=LEFT, fill=X)
button2.pack(side=LEFT, fill=X)
button3.pack(side=LEFT, fill=X)
button4.pack(side=LEFT, fill=X)

label = Label(bottom_frame, text="Hello", bg="black", fg="white")
label.pack(side=LEFT, fill=X)'''

'''name_label = Label(root, text="Name")
password_label = Label(root, text="Password")
Entry1 = Entry(root)
Entry2 = Entry(root)

name_label.grid(row=0, sticky=E)
password_label.grid(row=1, sticky=E)
Entry1.grid(row=0, column=1)
Entry2.grid(row=1, column=1)

check_box = Checkbutton(root, text="keep me logged in")
check_box.grid(columnspan=2)'''


'''def left_click(event):
    print "left"


def middle_click(event):
    print "middle"


def right_click(event):
    print "right"

frame = Frame(root, width=300, height=250)
frame.bind("<Button-1>", left_click)
frame.bind("<Button-2>", middle_click)
frame.bind("<Button-3>", right_click)
frame.pack()

#makes sure window is constantly displays
root.mainloop()'''


class ChatUI:

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        self.print_button = Button(frame, text="hello", command=self.print_message)
        self.print_button.pack(side=LEFT)

    def print_message(self):
        print "wow"


root = Tk()
ui = ChatUI(root)
root.mainloop()