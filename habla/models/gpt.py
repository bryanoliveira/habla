import os
from typing import Iterator

import openai
import tiktoken
from habla.models import BaseModel


class OpenAIModel(BaseModel):
    def __init__(
        self,
        system_message: str,
        model: str = "gpt-3.5-turbo",
        max_tokens=2048,
        stream=False,
    ) -> None:
        self.system_message = system_message
        self.model = model
        self.max_tokens = max_tokens
        self.stream = stream
        self.reset_conversation()

        openai.organization = os.getenv("OPENAI_ORG_ID")
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def reset_conversation(self):
        """Resets the conversation to just the system message."""
        self.conversation = [
            {
                "role": "system",
                "content": self.system_message,
            }
        ]

    def add_message(self, message: str, role: str):
        """Adds a message from the human or AI to the conversation."""
        assert role in [
            "user",
            "assistant",
        ], "role must be either 'user' or 'assistant'"

        self.conversation.append({"role": role, "content": message})

    def get_conversation(self) -> str:
        return "".join([f"{m['role']}: {m['content']}" for m in self.conversation])

    def count_tokens(self, text: str) -> int:
        encoding = tiktoken.encoding_for_model(self.model)
        return len(encoding.encode(text))

    def respond(self) -> Iterator:
        assert len(self.conversation) > 0, "conversation must not be empty"
        assert (
            self.conversation[-1]["role"] == "user"
        ), "last message must be from a human"

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.conversation,
            max_tokens=self.max_tokens,
            stream=self.stream,
        )
        if self.stream:
            for event in response:
                event = event.to_dict()
                if (
                    "choices" in event
                    and len(event["choices"]) > 0
                    and "delta" in event["choices"][0]
                ):
                    yield event["choices"][0]["delta"]["content"]
                else:
                    raise RuntimeError(f"Unknown event {event}")
        else:
            response = response.to_dict()
            if "choices" in response and len(response["choices"]) > 0:
                yield response["choices"][0]["message"]["content"]
            else:
                raise RuntimeError(f"Unknown response {response}")


if __name__ == "__main__":
    model = OpenAIModel("Hello, world!")
