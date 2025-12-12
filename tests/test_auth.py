import pytest
from fastapi import status


def test_login_success(client, clean_db):
    """Test successful admin login."""
    # Create org first
    client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "admin@testorg.com",
            "password": "securepass123"
        }
    )
    
    # Login
    response = client.post(
        "/admin/login",
        json={
            "email": "admin@testorg.com",
            "password": "securepass123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_email(client, clean_db):
    """Test login with invalid email."""
    response = client.post(
        "/admin/login",
        json={
            "email": "nonexistent@test.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in response.json()["detail"].lower()


def test_login_invalid_password(client, clean_db):
    """Test login with invalid password."""
    # Create org first
    client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "admin@testorg.com",
            "password": "securepass123"
        }
    )
    
    # Login with wrong password
    response = client.post(
        "/admin/login",
        json={
            "email": "admin@testorg.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in response.json()["detail"].lower()

