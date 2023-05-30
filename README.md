# Habla

Habla is an assistant that helps you with your software development projects. It scans your codebase and uses AI to answer questions and fulfill requests about it.

## Usage

To use Habla, install it with:

```bash
pip install git+https://github.com/bryanoliveira/habla --upgrade
```

Then, run it from any software development project with

```bash
habla
```

It will scan your current directory for relevant .py, .js and other text files, and use that context to understand your project.

You can then type in requests, for example:

> Explain the utils.py module

Habla will process your request and use Anthropic's API to generate a relevant response based on the context and request.

You can clear Habla's mind with the /clear command, and it will forget past messages in the current conversation.

## Requirements

- Python 3.8+ 
- An API key from Anthropic.co to access their AI models.
- The som Python libraries, installable with pip install -r requirements.txt

---
This README was generated using `habla` itself!