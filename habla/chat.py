import argparse
from colorama import Fore, Style
import logging
import os
import anthropic
from habla import scanner
from habla.utils import typewrite


LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL)


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
        + " You are Hablador, an expert in any kind of software development. Consider this project source:\n"
        + context
        + "\n"
        + "Fulfill this request: "
    )
    conversation = [original_message]
    # chat loop
    while True:
        user_input = input(f"{Fore.GREEN}You:{Style.RESET_ALL} ").strip()
        # commands
        if user_input == "/clear":
            conversation = [original_message]
            print("--- Mind cleared. Project context reloaded. ---", flush=True)
            continue

        # add message to conversation, generate prompt, and get streamed response
        conversation[-1] += user_input
        conversation.append(anthropic.AI_PROMPT)
        prompt = "".join(conversation)
        stream = client.completion_stream(
            prompt=prompt,
            stop_sequences=[anthropic.HUMAN_PROMPT],
            max_tokens_to_sample=400,
            model="claude-instant-v1-100k",
            stream=True,
        )
        # print streamed response, token by token
        print(f"\n{Fore.BLUE}Hablador:{Style.RESET_ALL}", end="", flush=True)
        response = ""
        for event in stream:
            intermediate_text = event["completion"]
            print(intermediate_text[len(response):], end="", flush=True)
            response = intermediate_text
        print("\n")
        # configure conversation for next iteration
        conversation[-1] += response
        conversation.append(anthropic.HUMAN_PROMPT + " ")

if __name__ == "__main__":
    main()
