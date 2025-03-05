from datetime import datetime
from pydantic import BaseModel

class ServerData(BaseModel):
    server_ulid: str
    timestamp: datetime
    temperature: float | None = None
    humidity: float | None = None
    voltage: float | None = None
    current: float | None = None
