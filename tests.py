import datetime
from Tkinter import *

root = Tk()

username = StringVar()
username.set(raw_input("enter"))


def main():
    if re.match("^[a-zA-Z0-9_.-]{4,12}$", username.get()):
        print 'hello'
    else:
        print 'wtf'

if __name__ == '__main__':
    main()



