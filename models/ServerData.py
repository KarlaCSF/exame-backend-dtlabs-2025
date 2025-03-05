from datetime import datetime
from pydantic import BaseModel, model_validator
from typing_extensions import Self
from enum import Enum

class ServerData(BaseModel):
    server_ulid: str
    timestamp: datetime
    temperature: float | None = None
    humidity: float | None = None
    voltage: float | None = None
    current: float | None = None

    @model_validator(mode='after')
    def check_at_least_one_measurement(self) -> Self:
        if not any([self.temperature, self.humidity, self.voltage, self.current]):
            raise ValueError('At least one sensor value must be provided')
        return self

class SensorType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    VOLTAGE = "voltage"
    CURRENT = "current"