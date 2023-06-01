import argparse
from copy import copy
import logging
import os
from typing import Tuple
from habla.ignorer import extended_ignore, is_human_readable


LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL)


def recursive_scan(
    original_path: str, current_path: str, max_depth: int, ignore_files: list = []
) -> Tuple[int, str]:
    total_characters = 0
    context = ""

    if os.path.isfile(current_path):
        if current_path == original_path:
            rel_path = os.path.relpath(current_path, os.path.dirname(original_path))
        else:
            rel_path = os.path.relpath(current_path, original_path)

        if is_human_readable(current_path):
            try:
                with open(current_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    total_characters = len(content)
                    logging.debug(f"{total_characters} characters in {rel_path}")

                    context = f"\n\n--- Contents of file {rel_path} ({total_characters} characters) ---\n```\n"
                    context += content
                    context += "\n```\n--- End of file " + rel_path + " ---"
            except PermissionError:
                pass

        return total_characters, context

    # current_path is a folder

    elif max_depth == 0:
        return total_characters, context
    
    for ignore_file in [".gitignore", ".hablaignore"]:
        ignore_file_path = os.path.join(current_path, ignore_file)
        if os.path.isfile(ignore_file_path):
            logging.info(f"Using {ignore_file_path} to ignore files.")
            ignore_files.append(ignore_file_path)

    try:
        for child in os.listdir(current_path):
            child_path = os.path.join(current_path, child)

            if any(extended_ignore(f)(child_path) for f in ignore_files):
                continue

            n, c = recursive_scan(
                original_path, child_path, max_depth - 1, copy(ignore_files)
            )
            total_characters += n
            context += c
    except PermissionError:
        pass

    return total_characters, context


def main():
    """Main function to parse command-line arguments and start scanning."""
    parser = argparse.ArgumentParser(
        description="Scan a repository for human-readable files."
    )
    parser.add_argument(
        "-p", "--path", help="Path to the repository or file (optional)", default=os.getcwd()
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        help="Maximum depth to scan (optional)",
        default=10,
        type=int,
    )
    args = parser.parse_args()

    total_characters, context = recursive_scan(args.path, args.path, args.max_depth)
    print(f"Total number of characters in the repository: {total_characters}")
    print(context)


if __name__ == "__main__":
    main()
