from pydantic import BaseModel


class ReceiveMessage(BaseModel):
    receiver: str
    text: str


class SendMessage(ReceiveMessage):
    sender: str
