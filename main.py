from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Literal
from models.ServerData import ServerData, SensorType
from prisma import Prisma
from ulid import ULID

db = Prisma()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)


@app.post("/data")
async def register_data(serverData: ServerData):
    data = await db.serverdata.create(data=serverData.model_dump())
    return data


@app.get("/data")
async def get_data(
    server_ulid: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    sensor_type: SensorType | None = None,
    aggregation: Literal["minute", "hour", "day"] | None = None,
):
    filters = {}
    if server_ulid:
        filters["server_ulid"] = server_ulid
    if start_time:
        filters.setdefault("timestamp", {})["gte"] = start_time
    if end_time:
        filters.setdefault("timestamp", {})["lte"] = end_time
    if sensor_type:
        filters[sensor_type.value] = {"not": None}

    if not aggregation:
        raw_data = await db.serverdata.find_many(
            where=filters,
        )

        return [
            {
                "timestamp": item.timestamp,
                **{
                    sensor.value: getattr(item, sensor.value)
                    for sensor in SensorType
                    if getattr(item, sensor.value) is not None
                },
            }
            for item in raw_data
        ]

    if sensor_type:
        sensor_columns = f"AVG({sensor_type.value}) AS {sensor_type.value}"
        having_clause = f"HAVING AVG({sensor_type.value}) IS NOT NULL"

    else:
        sensor_columns = """
            AVG(temperature) AS temperature,
            AVG(humidity) AS humidity,
            AVG(voltage) AS voltage,
            AVG(current) AS current"""

        having_clause = """
            HAVING
                AVG(temperature) IS NOT NULL OR
                AVG(humidity) IS NOT NULL OR
                AVG(voltage) IS NOT NULL OR
                AVG(current) IS NOT NULL
        """

    query = f"""
    SELECT 
        date_trunc('{aggregation}', timestamp) AS timestamp,
        { sensor_columns }
    FROM "ServerData"
    WHERE
        ($1::text IS NULL OR server_ulid = $1::text)
        AND ($2::timestamp IS NULL OR timestamp >= $2::timestamp)
        AND ($3::timestamp IS NULL OR timestamp <= $3::timestamp)
    GROUP BY timestamp
    { having_clause }
    ORDER BY timestamp;
    """

    params = [server_ulid, start_time, end_time]
    filtered_result = await db.query_raw(query, *params)

    formatted_result = []
    for item in filtered_result:
        sensor_data = {}
        for key, value in item.items():
            if value is not None:
                sensor_data[key] = value

        formatted_result.append(sensor_data)

    return formatted_result


@app.post("/servers")
async def create_server(server_name: str):
    ulid = str(ULID())

    server = await db.server.create(data={"ulid": ulid, "name": server_name})

    return server


async def is_online(server_id):
    return await db.serverdata.find_first(
        where={
            "server_ulid": server_id,
            "timestamp": {"gte": datetime.now() - timedelta(days=10)},
        }
    )

@app.get("/health/all")
async def get_all_servers():
    result = await db.server.find_many()

    response = []
    for item in result:
        item = item.model_dump(exclude_none=True)
        item["status"] = "online" if await is_online(item['ulid']) else "offline"
        response.append(item)

    return response

@app.get("/health/{server_id}")
async def get_server(server_id: str):
    status = "online" if await is_online(server_id) else "offline"

    result = await db.server.find_first(where={"ulid": server_id})

    if not result:
        return {"error": "Server not found"}

    response = result.model_dump(exclude_none=True)
    response["status"] = status

    return response
