import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "healthai_exercises")

client: AsyncIOMotorClient = None


def get_client() -> AsyncIOMotorClient:
    return client


def get_db():
    return client[MONGO_DB]
