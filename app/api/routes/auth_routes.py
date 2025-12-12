from fastapi import APIRouter, HTTPException, status
from app.models.schemas import LoginRequest, TokenResponse, ErrorResponse
from app.services.org_service import OrgService
from app.auth.jwt_handler import create_access_token
from datetime import timedelta

router = APIRouter(prefix="/admin", tags=["authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest):
    admin_data = await OrgService.authenticate_admin(request.email, request.password)
    
    if not admin_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token_data = {
        "admin_id": admin_data["admin_id"],
        "organization_name": admin_data["organization_name"],
        "email": admin_data["email"]
    }
    
    access_token = create_access_token(data=token_data)
    
    return TokenResponse(access_token=access_token, token_type="bearer")

