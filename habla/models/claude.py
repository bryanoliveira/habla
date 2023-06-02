import os
from typing import Optional, Union, Iterator

import anthropic
from habla.models import BaseModel


class AnthropicModel(BaseModel):
    def __init__(
        self,
        system_message,
        model="claude-instant-v1-100k",
        max_tokens=2048,
        stream=False,
    ):
        self.system_message = system_message
        self.model = model
        self.max_tokens = max_tokens
        self.stream = stream
        self.client = anthropic.Client(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.reset_conversation()

    def count_tokens(self, text: str) -> int:
        return anthropic.count_tokens(text)

    def respond(self) -> Iterator:
        assert len(self.conversation) > 0, "conversation must not be empty"
        assert self.conversation[-1].startswith(
            anthropic.HUMAN_PROMPT
        ), "last message must be from a human"

        prompt = "".join(self.conversation) + anthropic.AI_PROMPT
        response = self.client.completion_stream(
            prompt=prompt,
            stop_sequences=[anthropic.HUMAN_PROMPT],
            max_tokens_to_sample=self.max_tokens,
            model=self.model,
            stream=self.stream,
        )
        for event in response:
            if "completion" in event:
                yield event["completion"]
            else:
                raise RuntimeError(f"Unknown event {event}")

    def reset_conversation(self):
        """Resets the conversation to just the system message."""
        self.conversation = [
            f"{anthropic.HUMAN_PROMPT} {self.system_message}",
        ]

    def add_message(self, message: str, role: str):
        """Adds a message from the human or AI to the conversation."""
        assert role in ["human", "ai"], "role must be either 'human' or 'ai'"

        if len(self.conversation) == 1:
            # only system message
            self.conversation[-1] += message
        else:
            # subsequent messages
            self.conversation.append(
                {
                    "human": anthropic.HUMAN_PROMPT + " ",
                    "ai": anthropic.AI_PROMPT + " ",
                }[role]
                + message
            )
