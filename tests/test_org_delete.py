import pytest
from fastapi import status


def test_delete_org_unauthorized(client, clean_db):
    """Test deleting organization without authentication."""
    # Create org first
    client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "admin@testorg.com",
            "password": "securepass123"
        }
    )
    
    # Try to delete without token
    response = client.delete(
        "/org/delete",
        json={"organization_name": "TestOrg"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_org_success(client, clean_db):
    """Test successful organization deletion with valid token."""
    # Create org
    create_response = client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "admin@testorg.com",
            "password": "securepass123"
        }
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    
    # Login
    login_response = client.post(
        "/admin/login",
        json={
            "email": "admin@testorg.com",
            "password": "securepass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Delete org
    response = client.delete(
        "/org/delete",
        json={"organization_name": "TestOrg"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "deleted successfully" in response.json()["message"].lower()
    
    # Verify org is deleted
    get_response = client.get("/org/get?organization_name=TestOrg")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_org_wrong_admin(client, clean_db):
    """Test that admin can only delete their own organization."""
    # Create two orgs
    client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg1",
            "email": "admin1@test.com",
            "password": "securepass123"
        }
    )
    
    client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg2",
            "email": "admin2@test.com",
            "password": "securepass123"
        }
    )
    
    # Login as admin1
    login_response = client.post(
        "/admin/login",
        json={
            "email": "admin1@test.com",
            "password": "securepass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Try to delete TestOrg2 with admin1's token
    response = client.delete(
        "/org/delete",
        json={"organization_name": "TestOrg2"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

