import datetime
from Tkinter import *
import time
import datetime

'''root = Tk()

username = StringVar()
username.set(raw_input("enter"))'''


def main():
    """
    tests
    """
    '''cur_time = time.strftime("%H:%M")
    print cur_time

    hour, minute, second = cur_time.split(":")
    expired_time = datetime.timedelta(seconds=10) + datetime.timedelta(hours=int(hour), minutes=int(minute), seconds=int(second))
    print expired_time



    expired_time = datetime.datetime.strptime(expired_time, "%H:%M:%S")
    if expired_time > datetime.datetime.now().time():
        print "NICE" '''

    time_now = time.strftime("%H:%M")
    hour, minute = time_now.split(":")
    time_now = datetime.timedelta(hours=int(hour), minutes=int(minute))

    stats = [["user1", "10:00", "12:00", 0], ["user2", "10:00", "11:00", 0], ["user3", "10:00", "13:00", 0]]
    _count = 0
    for clients_list in stats:
        s_time = clients_list[1]
        s_time = datetime.datetime.strptime(s_time, '%H:%M')

        e_time = clients_list[2]
        e_time = datetime.datetime.strptime(e_time, '%H:%M')

        stats[_count][3] = e_time - s_time
        _count += 1
    print stats
    stats.sort(key=lambda lst: lst[3])

    '''for client_tuple in stats:
        s_time = client_tuple[1]
        hour, minute = s_time.split(":")
        s_time = datetime.timedelta(hours=int(hour), minutes=int(minute))

        e_time = client_tuple[2]
        hour, minute = e_time.split(":")
        e_time = datetime.timedelta(hours=int(hour), minutes=int(minute))'''

    print stats


if __name__ == '__main__':
    main()


