import argparse
import logging
import os
import anthropic
from habla import scanner
from habla.utils import typewrite


logging.basicConfig(level=logging.INFO)


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
    logging.info(f"Total number of characters in the repository: {total_characters}")

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

    while True:
        user_input = input("You: ")
        prompt = (
            anthropic.HUMAN_PROMPT
            # + " Consider this project source:\n"
            # + context + "\n"
            + "Fulfill this request: "
            + user_input
            + anthropic.AI_PROMPT
        )
        response = client.completion_stream(
            prompt=prompt,
            stop_sequences=[anthropic.HUMAN_PROMPT],
            max_tokens_to_sample=300,
            model="claude-instant-v1-100k",
            stream=True,
        )
        for event in response:
            print("\rHabla: " + event["completion"], end="")
        break


if __name__ == "__main__":
    main()
