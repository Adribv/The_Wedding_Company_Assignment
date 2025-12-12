from typing import List, Dict, Optional
from app.db.mongo import get_org_database


class OrgRepository:
    """Repository for organization-specific collection operations."""
    
    @staticmethod
    async def create_collection(collection_name: str) -> bool:
        """
        Create an empty collection for an organization.
        Returns True if successful, False otherwise.
        """
        try:
            db = await get_org_database(collection_name)
            # Create collection by inserting and deleting a dummy document
            await db[collection_name].insert_one({"_temp": True})
            await db[collection_name].delete_one({"_temp": True})
            return True
        except Exception:
            return False
    
    @staticmethod
    async def collection_exists(collection_name: str) -> bool:
        """Check if a collection exists."""
        try:
            db = await get_org_database(collection_name)
            collections = await db.list_collection_names()
            return collection_name in collections
        except Exception:
            return False
    
    @staticmethod
    async def migrate_collection(old_collection_name: str, new_collection_name: str) -> bool:
        """
        Migrate all documents from old collection to new collection.
        Returns True if successful, False otherwise.
        """
        try:
            db = await get_org_database(old_collection_name)
            
            # Check if old collection exists
            if not await OrgRepository.collection_exists(old_collection_name):
                return True  # Nothing to migrate
            
            # Get all documents from old collection
            old_collection = db[old_collection_name]
            cursor = old_collection.find({})
            documents = []
            async for doc in cursor:
                documents.append(doc)
            
            # If no documents, just create the new collection
            if not documents:
                await OrgRepository.create_collection(new_collection_name)
                return True
            
            # Insert all documents into new collection
            new_collection = db[new_collection_name]
            if documents:
                await new_collection.insert_many(documents)
            
            return True
        except Exception as e:
            print(f"Migration error: {e}")
            return False
    
    @staticmethod
    async def drop_collection(collection_name: str) -> bool:
        """Drop an organization collection."""
        try:
            db = await get_org_database(collection_name)
            await db.drop_collection(collection_name)
            return True
        except Exception:
            return False
    
    @staticmethod
    async def get_collection_document_count(collection_name: str) -> int:
        """Get the number of documents in a collection."""
        try:
            db = await get_org_database(collection_name)
            collection = db[collection_name]
            return await collection.count_documents({})
        except Exception:
            return 0
    
    @staticmethod
    async def list_collections() -> List[str]:
        """List all organization collections (for management)."""
        try:
            db = await get_org_database("")
            collections = await db.list_collection_names()
            # Filter to only org_* collections
            return [c for c in collections if c.startswith("org_")]
        except Exception:
            return []

