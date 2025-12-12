from typing import Optional, Dict, List
from datetime import datetime
from bson import ObjectId
from app.db.mongo import get_master_database
from app.models.schemas import AdminInfo, OrgMetadata


class MasterRepository:
    """Repository for master database operations."""
    
    @staticmethod
    async def get_organizations_collection():
        """Get the organizations collection from master DB."""
        db = await get_master_database()
        return db.organizations
    
    @staticmethod
    async def get_admins_collection():
        """Get the admins collection from master DB."""
        db = await get_master_database()
        return db.admins
    
    @staticmethod
    async def find_organization_by_name(organization_name: str) -> Optional[Dict]:
        """Find organization by name (case-insensitive)."""
        collection = await MasterRepository.get_organizations_collection()
        org = await collection.find_one(
            {"organization_name": {"$regex": f"^{organization_name}$", "$options": "i"}}
        )
        if org:
            org["_id"] = str(org["_id"])
        return org
    
    @staticmethod
    async def create_organization(org_data: Dict) -> Dict:
        """Create a new organization record in master DB."""
        collection = await MasterRepository.get_organizations_collection()
        org_data["created_at"] = datetime.utcnow()
        result = await collection.insert_one(org_data)
        org_data["_id"] = str(result.inserted_id)
        return org_data
    
    @staticmethod
    async def update_organization(organization_name: str, update_data: Dict) -> Optional[Dict]:
        """Update organization metadata."""
        collection = await MasterRepository.get_organizations_collection()
        result = await collection.find_one_and_update(
            {"organization_name": {"$regex": f"^{organization_name}$", "$options": "i"}},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result
    
    @staticmethod
    async def delete_organization(organization_name: str) -> bool:
        """Delete organization from master DB."""
        collection = await MasterRepository.get_organizations_collection()
        result = await collection.delete_one(
            {"organization_name": {"$regex": f"^{organization_name}$", "$options": "i"}}
        )
        return result.deleted_count > 0
    
    @staticmethod
    async def create_admin(admin_data: Dict) -> Dict:
        """Create a new admin user."""
        collection = await MasterRepository.get_admins_collection()
        result = await collection.insert_one(admin_data)
        admin_data["_id"] = str(result.inserted_id)
        return admin_data
    
    @staticmethod
    async def find_admin_by_email(email: str) -> Optional[Dict]:
        """Find admin by email."""
        collection = await MasterRepository.get_admins_collection()
        admin = await collection.find_one({"email": email.lower()})
        if admin:
            admin["_id"] = str(admin["_id"])
        return admin
    
    @staticmethod
    async def find_admin_by_org(organization_name: str) -> Optional[Dict]:
        """Find admin by organization name."""
        collection = await MasterRepository.get_admins_collection()
        admin = await collection.find_one(
            {"organization_name": {"$regex": f"^{organization_name}$", "$options": "i"}}
        )
        if admin:
            admin["_id"] = str(admin["_id"])
        return admin
    
    @staticmethod
    async def update_admin(admin_id: str, update_data: Dict) -> Optional[Dict]:
        """Update admin user."""
        collection = await MasterRepository.get_admins_collection()
        result = await collection.find_one_and_update(
            {"_id": ObjectId(admin_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result
    
    @staticmethod
    async def delete_admin_by_org(organization_name: str) -> bool:
        """Delete admin by organization name."""
        collection = await MasterRepository.get_admins_collection()
        result = await collection.delete_one(
            {"organization_name": {"$regex": f"^{organization_name}$", "$options": "i"}}
        )
        return result.deleted_count > 0
    
    @staticmethod
    async def list_all_organizations() -> List[Dict]:
        """List all organizations (for management)."""
        collection = await MasterRepository.get_organizations_collection()
        cursor = collection.find({})
        orgs = []
        async for org in cursor:
            org["_id"] = str(org["_id"])
            orgs.append(org)
        return orgs

