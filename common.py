#COMMANDS:
CHAT_MESSAGE = '01'
ADD_ADMIN = '02'
KICK_USER = '03'
MUTE_USER = '04'
PRIVATE_MESSAGE = '05'


def integer_to_2bytes_str(num):
    """
    The functions returns a string of 2 bytes
    according to the protocol. Example: from 5 to '05'
    """

    if num < 10:
        return '0' + str(num)
    else:
        return str(num)


def integer_to_3bytes_str(num):
    """
    The functions returns a string of 3 bytes
    according to the protocol. Example: from 5 to '005'
    """

    if num < 10:
        return '00' + str(num)
    elif num < 100:
        return '0' + str(num)
    else:
        return str(num)


def main():

    assert integer_to_2bytes_str(12) == '12', 'wrong'


if __name__ == '__main__':
    main()