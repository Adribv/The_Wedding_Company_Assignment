import pytest
from fastapi import status


def test_create_org_success(client, clean_db):
    """Test successful organization creation."""
    response = client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "admin@testorg.com",
            "password": "securepass123"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["message"] == "Organization created successfully"
    assert data["organization"]["organization_name"] == "TestOrg"
    assert data["organization"]["collection_name"].startswith("org_")
    assert data["organization"]["admin"]["email"] == "admin@testorg.com"


def test_create_org_duplicate_name(client, clean_db):
    """Test creating organization with duplicate name."""
    # Create first org
    client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "admin@testorg.com",
            "password": "securepass123"
        }
    )
    
    # Try to create duplicate
    response = client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "admin2@testorg.com",
            "password": "securepass123"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()


def test_create_org_case_insensitive_duplicate(client, clean_db):
    """Test that organization names are case-insensitive."""
    # Create first org
    client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "admin@testorg.com",
            "password": "securepass123"
        }
    )
    
    # Try to create with different case
    response = client.post(
        "/org/create",
        json={
            "organization_name": "testorg",
            "email": "admin2@testorg.com",
            "password": "securepass123"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()

