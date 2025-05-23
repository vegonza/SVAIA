from typing import TypedDict


class ChatMessage(TypedDict):
    role: str
    content: str

class File(TypedDict):
    name: str
    content: str
