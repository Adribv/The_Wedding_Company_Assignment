from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import settings

# Singleton MongoDB client
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def get_mongo_client() -> AsyncIOMotorClient:
    """Get or create MongoDB client singleton."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_url)
    return _client


async def get_master_database() -> AsyncIOMotorDatabase:
    """Get master database instance."""
    global _database
    if _database is None:
        client = await get_mongo_client()
        _database = client[settings.mongodb_db_name]
    return _database


async def get_org_database(org_collection_name: str) -> AsyncIOMotorDatabase:
    """Get organization-specific database (uses same DB, different collection)."""
    client = await get_mongo_client()
    return client[settings.mongodb_db_name]


async def close_mongo_connection():
    """Close MongoDB connection."""
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None

