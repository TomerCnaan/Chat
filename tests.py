import datetime


def main():
    print datetime.datetime.now().time().strftime("%H:%M") + "hey"


if __name__ == '__main__':
    main()