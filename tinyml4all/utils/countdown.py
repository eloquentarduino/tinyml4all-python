from time import sleep


def countdown():
    """
    Ask for user confirmation to proceed.
    Run a countdown.
    :return:
    """
    input("Press [Enter] when you're ready to start: ")
    print("Task will start in ", end="")

    for i in range(3, 0, -1):
        print(f"{i}...", end="")
        sleep(1)

    print("START!")
