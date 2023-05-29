import magic
import os
from pathlib import Path
from gitignore_parser import rule_from_pattern, handle_negation


def extended_ignore(full_path, base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(full_path)
    rules = [
        rule_from_pattern(
            ".git/", base_path=Path(base_dir).resolve(), source=(full_path, 0)
        ),
        rule_from_pattern(
            "package-lock.json",
            base_path=Path(base_dir).resolve(),
            source=(full_path, 1),
        ),
    ]
    with open(full_path) as ignore_file:
        counter = 1
        for line in ignore_file:
            counter += 1
            line = line.rstrip("\n")
            rule = rule_from_pattern(
                line, base_path=Path(base_dir).resolve(), source=(full_path, counter)
            )
            if rule:
                rules.append(rule)
    if not any(r.negation for r in rules):
        return lambda file_path: any(r.match(file_path) for r in rules)
    else:
        # We have negation rules. We can't use a simple "any" to evaluate them.
        # Later rules override earlier rules.
        return lambda file_path: handle_negation(file_path, rules)


def is_human_readable(file_path):
    mime_type = magic.from_file(file_path, mime=True)
    if mime_type is not None and mime_type.startswith("text"):
        return True
    return False
