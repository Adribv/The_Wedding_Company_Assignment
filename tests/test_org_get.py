import pytest
from fastapi import status


def test_get_org_success(client, clean_db):
    """Test successful organization retrieval."""
    # Create org first
    create_response = client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "admin@testorg.com",
            "password": "securepass123"
        }
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    
    # Get org
    response = client.get("/org/get?organization_name=TestOrg")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["organization"]["organization_name"] == "TestOrg"
    assert data["organization"]["admin"]["email"] == "admin@testorg.com"


def test_get_org_not_found(client, clean_db):
    """Test getting non-existent organization."""
    response = client.get("/org/get?organization_name=NonExistent")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()

