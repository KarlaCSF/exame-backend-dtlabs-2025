from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum, auto
from typing import Literal
from models.ServerData import ServerData
from prisma import Prisma

db = Prisma()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()

app = FastAPI(lifespan=lifespan)


class SensorType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    VOLTAGE = "voltage"
    CURRENT = "current"

@app.post("/data")
async def register_data(serverData: ServerData):    
    data = await db.serverdata.create(data=serverData.model_dump())
    return data


@app.get("/data")
def read_data(
    server_ulid: str | None = None, 
    start_time: datetime | None = None, 
    end_time: datetime | None = None, 
    sensor_type: SensorType | None = None, 
    aggregation: Literal["minute", "hour", "day"] | None = None
):
    pass