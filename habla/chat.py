import argparse
import atexit
from colorama import Fore, Style
import logging
import readline
import os
from threading import Thread
import time

import anthropic
from rich.console import Console
from rich.markdown import Markdown

from habla import scanner
from habla.utils import typewrite


LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL)

history_file = os.path.join(os.path.expanduser("~"), ".habla_history")
readline.read_history_file(history_file)
readline.parse_and_bind("tab: complete")
readline.set_history_length(1000)
atexit.register(readline.write_history_file, history_file)


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
        "-s", "--stream", help="Stream the assistant response", action="store_true"
    )
    parser.add_argument(
        "-t",
        "--max-tokens",
        help="Maximum tokens on the assistant's response",
        default=400,
        type=int,
    )
    parser.add_argument(
        "-m",
        "--model",
        help="The Anthropic model to use.",
        default="claude-instant-v1-100k",
        type=str,
    )
    args = parser.parse_args()

    # test api key
    client = anthropic.Client(api_key=os.environ["ANTHROPIC_API_KEY"])

    # scan the project for context
    total_characters, context = scanner.recursive_scan(
        args.path, args.path, args.max_depth
    )
    total_tokens = anthropic.count_tokens(context)
    logging.info(f"Total characters: {total_characters}")
    logging.info(f"Total tokens: {total_tokens}")
    if total_tokens > 95000 or total_characters > 80000:
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
    print("\n\n")

    # configure the conversation
    original_message = (
        anthropic.HUMAN_PROMPT
        + " You are Habla, an expert in any kind of software development. Consider this project source:\n"
        + context
        + "\n"
        + "Fulfill this kind request: "
    )
    conversation = [original_message]
    # chat loop
    console = Console()
    while True:
        print(f"\r{Fore.GREEN}You:{Style.RESET_ALL} ", end="", flush=True)
        user_input = input().strip()

        # commands
        if user_input == "/clear":
            conversation = [original_message]
            print("--- Mind cleared. Project context reloaded. ---", flush=True)
            continue

        # add message to conversation, generate prompt, and get streamed response
        conversation[-1] += user_input
        conversation.append(anthropic.AI_PROMPT)
        prompt = "".join(conversation)
        result = client.completion_stream(
            prompt=prompt,
            stop_sequences=[anthropic.HUMAN_PROMPT],
            max_tokens_to_sample=args.max_tokens,
            model=args.model,
            stream=args.stream,
        )
        # print streamed response, token by token
        if args.stream:
            response = ""
            print(f"\n{Fore.BLUE}Habla:{Style.RESET_ALL} ", end="", flush=True)
            for event in result:
                intermediate_text = event["completion"]
                print(intermediate_text[len(response) :], end="")
                response = intermediate_text
        else:
            stop_thread = False

            def show_spinning_bar():
                bar = ["|", "/", "-", "\\"]
                i = 0
                while not stop_thread:
                    print(
                        f"\r{Fore.BLUE}Habla:{Style.RESET_ALL} (Thinking... {bar[i % 4]})",
                        end="",
                        flush=True,
                    )
                    time.sleep(0.1)
                    i += 1

            # think
            print("")
            bar_thread = Thread(target=show_spinning_bar)
            bar_thread.start()
            response = next(result)["completion"]
            stop_thread = True
            bar_thread.join()
            # respond
            print(f"\r{Fore.BLUE}Habla:{Style.RESET_ALL}  ", end="", flush=True)
            console.print(Markdown(response))
        print("\n")
        # configure conversation for next iteration
        conversation[-1] += response
        conversation.append(anthropic.HUMAN_PROMPT + " ")


if __name__ == "__main__":
    main()
