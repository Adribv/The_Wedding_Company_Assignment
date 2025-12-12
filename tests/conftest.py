import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import create_app
from app.db.mongo import get_master_database, close_mongo_connection
from app.repositories.org_repo import OrgRepository
import os


@pytest.fixture(scope="function")
def test_app():
    """Create test FastAPI app."""
    # Override settings for testing
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
    os.environ["MONGODB_DB_NAME"] = "org_master_test"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    
    app = create_app()
    yield app
    
    # Cleanup
    asyncio.run(close_mongo_connection())


@pytest.fixture(scope="function")
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """Clean test database before and after each test."""
    # Clean before test
    async def _clean():
        db = await get_master_database()
        # Drop all collections
        collections = await db.list_collection_names()
        for collection_name in collections:
            await db.drop_collection(collection_name)
        # Also clean org collections
        org_collections = await OrgRepository.list_collections()
        for coll_name in org_collections:
            await OrgRepository.drop_collection(coll_name)
    
    asyncio.run(_clean())
    yield
    # Clean after test
    asyncio.run(_clean())

