import time


def notify(message, delay=None, columns=40):
    """Prints a notification on screen.

    :param str message: The message to display.

    :param delay: An optional delay, in seconds, before returning from this
        function
    :type delay: float or None

    :param int columns: The number of columns for the notification.
    """
    # The maximum length of a message line; we need four columns for the frame
    max_length = columns - 4

    # Split the message into lines containing at most max_length characters
    lines = []
    for word in message.split():
        if not lines or len(lines[-1]) + 1 + len(word) > max_length:
            lines.append(word)
        else:
            lines[-1] += ' ' + word

    # Print the message
    print('')
    print('+' + '=' * (columns - 2) + '+')
    for line in lines:
        print(('| {:<%ds} |' % max_length).format(line))
    print('+' + '-' * (columns - 2) + '+')

    if delay:
        time.sleep(delay)
