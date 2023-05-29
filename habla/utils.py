import time


def typewrite(text: str, speed=0.01):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(speed)
    print()
