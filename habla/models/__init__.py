from typing import Iterator

class BaseModel:
    def reset_conversation(self):
        raise NotImplementedError

    def add_message(self, message: str, role: str):
        raise NotImplementedError

    def get_conversation(self) -> str:
        raise NotImplementedError

    def count_tokens(self, text: str) -> int:
        raise NotImplementedError

    def respond(self) -> Iterator:
        raise NotImplementedError