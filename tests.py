import datetime
from Tkinter import *
import time
import datetime

'''root = Tk()

username = StringVar()
username.set(raw_input("enter"))'''


def main():
    cur_time = time.strftime("%H:%M:%S")
    print cur_time

    hour, minute, second = cur_time.split(":")
    expired_time = datetime.timedelta(seconds=10) + datetime.timedelta(hours=int(hour), minutes=int(minute), seconds=int(second))
    print expired_time

if __name__ == '__main__':
    main()



