import pytest
from fastapi import status


def test_update_org_rename_success(client, clean_db):
    """Test successful organization rename with collection migration."""
    # Create org
    create_response = client.post(
        "/org/create",
        json={
            "organization_name": "OldOrg",
            "email": "admin@oldorg.com",
            "password": "securepass123"
        }
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    old_collection_name = create_response.json()["organization"]["collection_name"]
    
    # Login
    login_response = client.post(
        "/admin/login",
        json={
            "email": "admin@oldorg.com",
            "password": "securepass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Update org name
    update_response = client.put(
        "/org/update",
        json={
            "organization_name": "OldOrg",
            "new_organization_name": "NewOrg"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert update_response.status_code == status.HTTP_200_OK
    data = update_response.json()
    assert data["organization"]["organization_name"] == "NewOrg"
    assert data["organization"]["collection_name"] != old_collection_name
    assert data["organization"]["collection_name"].startswith("org_")
    
    # Verify old name doesn't exist
    get_old_response = client.get("/org/get?organization_name=OldOrg")
    assert get_old_response.status_code == status.HTTP_404_NOT_FOUND
    
    # Verify new name exists
    get_new_response = client.get("/org/get?organization_name=NewOrg")
    assert get_new_response.status_code == status.HTTP_200_OK


def test_update_org_email(client, clean_db):
    """Test updating organization admin email."""
    # Create org
    client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "admin@testorg.com",
            "password": "securepass123"
        }
    )
    
    # Login
    login_response = client.post(
        "/admin/login",
        json={
            "email": "admin@testorg.com",
            "password": "securepass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Update email
    update_response = client.put(
        "/org/update",
        json={
            "organization_name": "TestOrg",
            "email": "newadmin@testorg.com"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["organization"]["admin"]["email"] == "newadmin@testorg.com"


def test_update_org_password(client, clean_db):
    """Test updating organization admin password."""
    # Create org
    client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "admin@testorg.com",
            "password": "oldpassword123"
        }
    )
    
    # Login with old password
    login_response = client.post(
        "/admin/login",
        json={
            "email": "admin@testorg.com",
            "password": "oldpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Update password
    update_response = client.put(
        "/org/update",
        json={
            "organization_name": "TestOrg",
            "password": "newpassword123"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert update_response.status_code == status.HTTP_200_OK
    
    # Verify old password doesn't work
    old_login_response = client.post(
        "/admin/login",
        json={
            "email": "admin@testorg.com",
            "password": "oldpassword123"
        }
    )
    assert old_login_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Verify new password works
    new_login_response = client.post(
        "/admin/login",
        json={
            "email": "admin@testorg.com",
            "password": "newpassword123"
        }
    )
    assert new_login_response.status_code == status.HTTP_200_OK

