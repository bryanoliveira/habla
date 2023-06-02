import argparse
import atexit
from colorama import Fore
import logging
import readline
import os
from threading import Thread
import time

from rich.console import Console
from rich.markdown import Markdown

from habla import scanner
from habla.utils import typewrite, print_divider


LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL)

history_file = os.path.join(os.path.expanduser("~"), ".habla_history")
readline.read_history_file(history_file)
readline.set_history_length(1000)
atexit.register(readline.write_history_file, history_file)

USER_PREFIX = f"You"
HABLA_PREFIX = f"Habla"
DEFAULT_SYSTEM_CLAUDE = (
    "You are Habla, an expert in any kind of software development"
    + " which always helps the Human with their requests and always provide examples of solutions."
    + " The source code the user is currently working with follows:\n{context}"
    + "\nCarefully read the code and fulfill the user's requests, responding with Markdown. The first request is: "
)
DEFAULT_SYSTEM_OPENAI = (
    "You are Habla, an expert in any kind of software development"
    + " which always helps the user with their requests and always provide examples of solutions."
    + " The source code the user is currently working with follows:\n{context}"
    + "\nCarefully read the code and fulfill the user's requests, responding with Markdown."
)


def main():
    parser = argparse.ArgumentParser(
        description="""A CLI tool to hablar with a project's code.
        It's an infinite loop that takes user input and
        returns a response considering the scanned context.
        Uses Anthropic's API and claude-instant-v1-100k to generate a response."""
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Path to the repository or file (optional, defaults to the current directory)",
        default=os.getcwd(),
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        help="Maximum depth to scan (optional, defaults to 10)",
        default=10,
        type=int,
    )
    parser.add_argument(
        "--stream",
        help="Stream the assistant response. Disables Markdown rendering.",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--max-tokens",
        help="Maximum tokens on the assistant's response (optional, defaults to 2048).",
        default=2048,
        type=int,
    )
    parser.add_argument(
        "-v",
        "--vendor",
        help="	The model vendor to use (Anthropic or OpenAI) (optional, defaults to anthropic).",
        default="anthropic",
        choices=["anthropic", "openai"],
        type=str,
    )
    parser.add_argument(
        "-m",
        "--model",
        help="The model to use (optional, defaults to claude-instant-v1-100k).",
        default="claude-instant-v1-100k",
        type=str,
    )
    parser.add_argument(
        "--system-message",
        help="The system message to start the conversation. See habla.chat.DEFAULT_SYSTEM_CLAUDE for an example.",
        default=DEFAULT_SYSTEM_CLAUDE,
        type=str,
    )
    parser.add_argument(
        "--use-anthropic",
        help="Use Anthropic models.",
        action="store_true",
    )
    parser.add_argument(
        "--use-openai",
        help="Use OpenAI models.",
        action="store_true",
    )
    args = parser.parse_args()

    if args.use_anthropic:
        args.vendor = "anthropic"
        args.system_message = DEFAULT_SYSTEM_CLAUDE
    if args.use_openai:
        args.vendor = "openai"
        args.system_message = DEFAULT_SYSTEM_OPENAI
        if args.model == "claude-instant-v1-100k":
            args.model = "gpt-3.5-turbo"
    logging.info(f"Using {args.vendor}'s {args.model}")

    # scan the project for context
    total_characters, context = scanner.recursive_scan(
        args.path, args.path, args.max_depth
    )
    logging.info(f"Total characters: {total_characters}")

    # initialize the model
    if args.vendor == "anthropic":
        from habla.models import claude

        model = claude.AnthropicModel(
            model=args.model,
            system_message=args.system_message.format(context=context),
            max_tokens=args.max_tokens,
            stream=args.stream,
        )
    elif args.vendor == "openai":
        from habla.models import gpt

        model = gpt.OpenAIModel(
            model=args.model,
            system_message=args.system_message.format(context=context),
            max_tokens=args.max_tokens,
            stream=args.stream,
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
    print("\n\n")
    print_divider(HABLA_PREFIX, Fore.BLUE)
    typewrite(
        f"Hello! I am Habla, an AI assistant powered by {args.vendor}'s {args.model} and created to help you with your {os.path.basename(os.getcwd()) }"
        " software project. How can I be of assistance today?\n",
        speed=0.003,
    )

    # chat loop
    console = Console()
    while True:
        # get user input and rewrite it parsing any markdown
        print_divider(USER_PREFIX, Fore.GREEN)
        user_input = input().strip()
        print(f"\033[F\033[K", end="")
        console.print(Markdown(f"{user_input}"))
        print()
        model.add_message(user_input, "user")

        # get streamed response
        result = model.respond()

        # print streamed response, token by token
        print_divider(HABLA_PREFIX, Fore.BLUE)
        if args.stream:
            response: str = ""
            for intermediate_text in result:
                typewrite(intermediate_text, end="")
                response += intermediate_text
            print("\n")
        else:
            stop_thread = False

            def show_spinning_bar():
                bar = ["|", "/", "-", "\\"]
                i = 0
                while not stop_thread:
                    print(
                        f"\r(Thinking... {bar[i % 4]})",
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
            print(f"\r", end="", flush=True)
            with console.capture() as capture:
                console.print(Markdown(response))
            typewrite(capture.get(), speed=0.001)

        # configure conversation for next iteration
        model.add_message(response, "assistant")


if __name__ == "__main__":
    main()
