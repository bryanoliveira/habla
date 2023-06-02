import time
import os
from colorama import Fore, Style


def typewrite(text: str, speed=0.01, end="\n"):
    """Print text character by character with time delay."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(speed)
    print("", end=end)


def print_divider(text: str, color=Fore.GREEN, divider_char="━"):
    cols = os.get_terminal_size().columns
    print(
        f"{Style.BRIGHT}{color}{text} "
        + divider_char * (cols - len(text) - 1)
        + f"{Style.RESET_ALL}\n",
        flush=True,
    )
