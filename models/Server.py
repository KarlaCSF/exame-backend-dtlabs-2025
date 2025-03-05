from pydantic import BaseModel
from ulid import ULID

class Server(BaseModel):
    ulid: ULID
    name: str
