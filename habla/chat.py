import argparse
import atexit
from colorama import Fore, Style
import logging
import readline
import os
from threading import Thread
import time

from rich.console import Console
from rich.markdown import Markdown

from habla import scanner
from habla.utils import typewrite


LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL)

history_file = os.path.join(os.path.expanduser("~"), ".habla_history")
readline.read_history_file(history_file)
readline.set_history_length(1000)
atexit.register(readline.write_history_file, history_file)

USER_PREFIX = f"{Fore.GREEN}You:{Style.RESET_ALL} "
HABLA_PREFIX = f"{Fore.BLUE}Habla:{Style.RESET_ALL} "


def main():
    parser = argparse.ArgumentParser(
        description="""A CLI tool to hablar with a project's code.
        It's an infinite loop that takes user input and
        returns a response considering the scanned context.
        Uses Anthropic's API and claude-instant-v1-100k to generate a response."""
    )
    parser.add_argument(
        "-p", "--path", help="Path to the repository (optional)", default=os.getcwd()
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        help="Maximum depth to scan (optional)",
        default=10,
        type=int,
    )
    parser.add_argument(
        "--stream", help="Stream the assistant response", action="store_true"
    )
    parser.add_argument(
        "-t",
        "--max-tokens",
        help="Maximum tokens on the assistant's response",
        default=2048,
        type=int,
    )
    parser.add_argument(
        "-v",
        "--vendor",
        help="The model vendor to use (Anthropic).",
        default="anthropic",
        choices=["anthropic"],
        type=str,
    )
    parser.add_argument(
        "-m",
        "--model",
        help="The model to use.",
        default="claude-instant-v1-100k",
        type=str,
    )
    parser.add_argument(
        "--system-message",
        help="The system message to start the conversation.",
        default="You are Habla, an expert in any kind of software development"
        + " which always helps the Human with their requests and always provide examples of solutions."
        + " Consider this project source:\n{context}"
        + "\nNow, fulfill this kind request: ",
        type=str,
    )
    args = parser.parse_args()

    # scan the project for context
    total_characters, context = scanner.recursive_scan(
        args.path, args.path, args.max_depth
    )
    logging.info(f"Total characters: {total_characters}")

    # initialize the model
    if args.vendor == "anthropic":
        from habla.models import claude

        model = claude.AnthropicModel(
            model=args.model, system_message=args.system_message.format(context=context)
        )
    else:
        raise ValueError(f"Unknown vendor {args.vendor}")

    # check if the project is too big
    total_tokens = model.count_tokens(context)
    logging.info(f"Total tokens: {total_tokens}")
    if total_tokens > 95000:
        logging.error(
            "Your project is too big to be scanned. "
            "Try to limit the depth of the scan with the -d option."
        )
        exit(1)

    # greetings!
    print("\n\n")
    typewrite(
        r"""    ___       ___       ___       ___       ___   
   /\__\     /\  \     /\  \     /\__\     /\  \  
  /:/__/_   /::\  \   /::\  \   /:/  /    /::\  \ 
 /::\/\__\ /::\:\__\ /::\:\__\ /:/__/    /::\:\__\
 \/\::/  / \/\::/  / \:\::/  / \:\  \    \/\::/  /
   /:/  /    /:/  /   \::/  /   \:\__\     /:/  / 
   \/__/     \/__/     \/__/     \/__/     \/__/  """,
        speed=0.002,
    )
    typewrite(
        f"\n\n{HABLA_PREFIX}Hello! I am Habla, an AI assistant created to help you with your {os.path.basename(os.getcwd()) }"
        " software project. How can I be of assistance today?\n",
        speed=0.003,
    )

    # chat loop
    console = Console()
    while True:
        # get user input and rewrite it parsing any markdown
        print(f"\r{USER_PREFIX}", end="", flush=True)
        user_input = input().strip()
        print(f"\033[F\033[K{USER_PREFIX}", end="")
        console.print(Markdown(f"{user_input}"))
        model.add_message(user_input, "human")

        # get streamed response
        result = model.respond()

        # print streamed response, token by token
        if args.stream:
            response: str = ""
            print(f"{HABLA_PREFIX}", end="", flush=True)
            for intermediate_text in result:
                print(intermediate_text[len(response) :], end="")
                response = intermediate_text
            print()
        else:
            stop_thread = False

            def show_spinning_bar():
                bar = ["|", "/", "-", "\\"]
                i = 0
                while not stop_thread:
                    print(
                        f"\r{HABLA_PREFIX}(Thinking... {bar[i % 4]})",
                        end="",
                        flush=True,
                    )
                    time.sleep(0.1)
                    i += 1

            # think
            bar_thread = Thread(target=show_spinning_bar)
            bar_thread.start()
            response = next(result)
            stop_thread = True
            bar_thread.join()
            # respond
            print(f"\r{HABLA_PREFIX}", end="", flush=True)
            with console.capture() as capture:
                console.print(Markdown(response))
            typewrite(capture.get(), speed=0.001)

        # configure conversation for next iteration
        model.add_message(response, "ai")


if __name__ == "__main__":
    main()
