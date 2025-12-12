from typing import Optional, Dict
from datetime import datetime
from bson import ObjectId
from app.repositories.master_repo import MasterRepository
from app.repositories.org_repo import OrgRepository
from app.utils.helpers import sanitize_organization_name, validate_collection_name
from app.auth.password import hash_password, verify_password
from app.models.schemas import OrgMetadata, AdminInfo


class OrgService:
    """Service layer for organization business logic."""
    
    @staticmethod
    async def create_organization(organization_name: str, email: str, password: str) -> Dict:
        existing = await MasterRepository.find_organization_by_name(organization_name)
        if existing:
            raise ValueError(f"Organization '{organization_name}' already exists")
        
        collection_name = sanitize_organization_name(organization_name)
        
        if not validate_collection_name(collection_name):
            raise ValueError(f"Invalid collection name generated: {collection_name}")
        
        if await OrgRepository.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' already exists")
        
        admin_id = str(ObjectId())
        hashed_password = hash_password(password)
        
        admin_data = {
            "_id": ObjectId(admin_id),
            "admin_id": admin_id,
            "email": email.lower(),
            "password": hashed_password,
            "organization_name": organization_name,
            "created_at": datetime.utcnow()
        }
        
        org_data = {
            "organization_name": organization_name,
            "collection_name": collection_name,
            "admin": {
                "admin_id": admin_id,
                "email": email.lower()
            },
            "created_at": datetime.utcnow()
        }
        
        try:
            await MasterRepository.create_admin(admin_data)
            org_record = await MasterRepository.create_organization(org_data)
            
            collection_created = await OrgRepository.create_collection(collection_name)
            if not collection_created:
                await MasterRepository.delete_organization(organization_name)
                await MasterRepository.delete_admin_by_org(organization_name)
                raise RuntimeError("Failed to create organization collection")
            
            return org_record
        except Exception as e:
            await MasterRepository.delete_organization(organization_name)
            await MasterRepository.delete_admin_by_org(organization_name)
            raise e
    
    @staticmethod
    async def get_organization(organization_name: str) -> Dict:
        """Get organization metadata."""
        org = await MasterRepository.find_organization_by_name(organization_name)
        if not org:
            raise ValueError(f"Organization '{organization_name}' not found")
        return org
    
    @staticmethod
    async def update_organization(
        organization_name: str,
        new_organization_name: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None
    ) -> Dict:
        """Update organization metadata and optionally rename/migrate collection."""
        # Get existing organization
        org = await MasterRepository.find_organization_by_name(organization_name)
        if not org:
            raise ValueError(f"Organization '{organization_name}' not found")
        
        update_data = {}
        admin_update_data = {}
        
        # Handle renaming
        if new_organization_name and new_organization_name.lower() != organization_name.lower():
            # Check if new name is available
            existing = await MasterRepository.find_organization_by_name(new_organization_name)
            if existing:
                raise ValueError(f"Organization '{new_organization_name}' already exists")
            
            # Sanitize new collection name
            new_collection_name = sanitize_organization_name(new_organization_name)
            old_collection_name = org["collection_name"]
            
            # Migrate collection
            migration_success = await OrgRepository.migrate_collection(
                old_collection_name,
                new_collection_name
            )
            
            if not migration_success:
                raise RuntimeError("Failed to migrate organization collection")
            
            # Drop old collection
            await OrgRepository.drop_collection(old_collection_name)
            
            # Update organization metadata
            update_data["organization_name"] = new_organization_name
            update_data["collection_name"] = new_collection_name
            admin_update_data["organization_name"] = new_organization_name
        
        # Handle email update
        if email:
            update_data["admin.email"] = email.lower()
            admin_update_data["email"] = email.lower()
        
        # Handle password update
        if password:
            hashed_password = hash_password(password)
            admin_update_data["password"] = hashed_password
        
        # Update organization record
        if update_data:
            updated_org = await MasterRepository.update_organization(organization_name, update_data)
            if not updated_org:
                raise RuntimeError("Failed to update organization")
            org = updated_org
        
        # Update admin record
        if admin_update_data:
            admin_id = org["admin"]["admin_id"]
            updated_admin = await MasterRepository.update_admin(admin_id, admin_update_data)
            if not updated_admin:
                raise RuntimeError("Failed to update admin")
        
        # Refresh org data to get latest state
        final_org_name = update_data.get("organization_name", organization_name)
        if final_org_name != organization_name or update_data:
            org = await MasterRepository.find_organization_by_name(final_org_name)
            if not org:
                raise RuntimeError("Failed to refresh organization data after update")
        
        return org
    
    @staticmethod
    async def delete_organization(organization_name: str) -> bool:
        """Delete organization and its collection."""
        # Get organization
        org = await MasterRepository.find_organization_by_name(organization_name)
        if not org:
            raise ValueError(f"Organization '{organization_name}' not found")
        
        collection_name = org["collection_name"]
        
        # Drop collection
        await OrgRepository.drop_collection(collection_name)
        
        # Delete admin
        await MasterRepository.delete_admin_by_org(organization_name)
        
        # Delete organization
        deleted = await MasterRepository.delete_organization(organization_name)
        
        return deleted
    
    @staticmethod
    async def authenticate_admin(email: str, password: str) -> Optional[Dict]:
        """Authenticate admin user and return admin data."""
        admin = await MasterRepository.find_admin_by_email(email)
        if not admin:
            return None
        
        if not verify_password(password, admin["password"]):
            return None
        
        # Get organization info
        org = await MasterRepository.find_organization_by_name(admin["organization_name"])
        if not org:
            return None
        
        return {
            "admin_id": admin["admin_id"],
            "email": admin["email"],
            "organization_name": admin["organization_name"],
            "org_data": org
        }

