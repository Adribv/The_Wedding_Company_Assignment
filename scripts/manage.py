#!/usr/bin/env python3
"""
Management CLI script for Organization Management Service.
Usage: python scripts/manage.py list-orgs
       python scripts/manage.py list-admins
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.mongo import get_master_database, close_mongo_connection
from app.repositories.master_repo import MasterRepository
from app.repositories.org_repo import OrgRepository


async def list_organizations():
    """List all organizations."""
    try:
        orgs = await MasterRepository.list_all_organizations()
        
        if not orgs:
            print("No organizations found.")
            return
        
        print(f"\nFound {len(orgs)} organization(s):\n")
        print(f"{'Organization Name':<30} {'Collection Name':<30} {'Admin Email':<30} {'Created At'}")
        print("-" * 100)
        
        for org in orgs:
            org_name = org.get("organization_name", "N/A")
            collection_name = org.get("collection_name", "N/A")
            admin_email = org.get("admin", {}).get("email", "N/A")
            created_at = org.get("created_at", "N/A")
            
            if isinstance(created_at, str):
                created_str = created_at
            else:
                created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else "N/A"
            
            print(f"{org_name:<30} {collection_name:<30} {admin_email:<30} {created_str}")
        
        print()
    except Exception as e:
        print(f"Error listing organizations: {e}")
    finally:
        await close_mongo_connection()


async def list_admins():
    """List all admin accounts."""
    try:
        db = await get_master_database()
        admins_collection = await MasterRepository.get_admins_collection()
        
        cursor = admins_collection.find({})
        admins = []
        async for admin in cursor:
            admin["_id"] = str(admin["_id"])
            admins.append(admin)
        
        if not admins:
            print("No admin accounts found.")
            return
        
        print(f"\nFound {len(admins)} admin account(s):\n")
        print(f"{'Admin ID':<30} {'Email':<30} {'Organization':<30} {'Created At'}")
        print("-" * 100)
        
        for admin in admins:
            admin_id = admin.get("admin_id", "N/A")
            email = admin.get("email", "N/A")
            org_name = admin.get("organization_name", "N/A")
            created_at = admin.get("created_at", "N/A")
            
            if isinstance(created_at, str):
                created_str = created_at
            else:
                created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else "N/A"
            
            print(f"{admin_id:<30} {email:<30} {org_name:<30} {created_str}")
        
        print()
    except Exception as e:
        print(f"Error listing admins: {e}")
    finally:
        await close_mongo_connection()


async def list_collections():
    """List all organization collections."""
    try:
        collections = await OrgRepository.list_collections()
        
        if not collections:
            print("No organization collections found.")
            return
        
        print(f"\nFound {len(collections)} collection(s):\n")
        
        db = await get_master_database()
        for collection_name in collections:
            collection = db[collection_name]
            count = await collection.count_documents({})
            print(f"  {collection_name:<40} ({count} documents)")
        
        print()
    except Exception as e:
        print(f"Error listing collections: {e}")
    finally:
        await close_mongo_connection()


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/manage.py <command>")
        print("Commands:")
        print("  list-orgs      - List all organizations")
        print("  list-admins    - List all admin accounts")
        print("  list-collections - List all organization collections")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list-orgs":
        asyncio.run(list_organizations())
    elif command == "list-admins":
        asyncio.run(list_admins())
    elif command == "list-collections":
        asyncio.run(list_collections())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

