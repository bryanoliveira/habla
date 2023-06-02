<pre align="center">
    ___       ___       ___       ___       ___   
   /\__\     /\  \     /\  \     /\__\     /\  \  
  /:/__/_   /::\  \   /::\  \   /:/  /    /::\  \ 
 /::\/\__\ /::\:\__\ /::\:\__\ /:/__/    /::\:\__\
 \/\::/  / \/\::/  / \:\::/  / \:\  \    \/\::/  /
   /:/  /    /:/  /   \::/  /   \:\__\     /:/  / 
   \/__/     \/__/     \/__/     \/__/     \/__/  
</pre>

Habla is an assistant that helps you with your software development projects. It scans your codebase and uses AI to answer questions and fulfill requests about it.

Habla is great for:

- Rapdly understanding how code written by third parties work
- Extending your code considering existing functions and style
- Identifying bugs in integrations and interactions between modules

Habla isn't so great with:

- Very large projects (its context size is limited by underlying models' context size)
- Knowing about the latest libs, or packages, as it's knowledge has a time cutoff.

## Usage

To use Habla, install it with:

```bash
pip install git+https://github.com/bryanoliveira/habla --upgrade
```

Set up your favorite model's keys:

```bash
export ANTHROPIC_API_KEY="<YOUR API KEY>"
# or
export OPENAI_API_KEY="<YOUR API KEY>"
export OPENAI_ORG_ID="<YOUR ORGANIZATION ID>"
```

Then, run it from any software development project with

```bash
habla
```

It will scan your current directory for relevant .py, .js and other text files, and use that context to understand your project.

You can then type in requests, for example:

> Explain the utils.py module

Habla will process your request and use Anthropic's or OpenAI's API to generate a relevant response based on the context and request.

### CLI Arguments

| Option                                             | Description                                                                                                             |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| -h, --help                                         | Show the help message and exit                                                                                          |
| -p PATH, --path PATH                               | Path to the repository or file (optional, defaults to the current directory)                                            |
| -d MAX_DEPTH, --max-depth MAX_DEPTH                | Maximum depth to scan (optional, defaults to `10`)                                                                      |
| --stream                                           | Stream the assistant response. Disables Markdown rendering.                                                             |
| -t MAX_TOKENS, --max-tokens MAX_TOKENS             | Maximum tokens on the assistant's response (optional, defaults to `2048`).                                              |
| -v {anthropic,openai}, --vendor {anthropic,openai} | The model vendor to use (Anthropic or OpenAI) (optional, defaults to `anthropic`).                                      |
| -m MODEL, --model MODEL                            | The model to use (optional, defaults to `claude-instant-v1-100k`).                                                      |
| --system-message SYSTEM_MESSAGE                    | The system message to start the conversation (optional, defaults to `habla.chat.DEFAULT_SYSTEM_CLAUDE`).                |
| --use-anthropic                                    | Use Anthropic models. Sets `vendor` to `anthropic` and uses the default `system_message` for Claude.                    |
| --use-openai                                       | Use OpenAI models. Sets `vendor` to `openai`, `model` to `gpt-3.5-turbo` and uses the default `system_message` for GPT. |

## Requirements

- Python 3.8+
- An API key from [Anthropic](https://console.anthropic.com) or [OpenAI](https://platform.openai.com) to access their AI models.
- Python libraries installable with `pip install -r requirements.txt`

---

This README was (mostly) generated using `habla` itself!
