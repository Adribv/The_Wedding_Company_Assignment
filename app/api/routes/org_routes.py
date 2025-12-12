from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import Optional
from app.models.schemas import (
    OrgCreateRequest, OrgCreateResponse,
    OrgGetRequest, OrgGetResponse,
    OrgUpdateRequest, OrgUpdateResponse,
    OrgDeleteRequest, OrgDeleteResponse,
    OrgMetadata, AdminInfo, ErrorResponse
)
from app.services.org_service import OrgService
from app.auth.jwt_handler import verify_token
from app.repositories.master_repo import MasterRepository

router = APIRouter(prefix="/org", tags=["organizations"])


async def get_current_admin(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return payload


def verify_org_access(organization_name: str, admin_payload: dict):
    admin_org = admin_payload.get("organization_name", "").lower()
    requested_org = organization_name.lower()
    
    if admin_org != requested_org:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this organization"
        )
    
    return admin_payload


@router.post("/create", response_model=OrgCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(request: OrgCreateRequest):
    try:
        org_data = await OrgService.create_organization(
            request.organization_name,
            request.email,
            request.password
        )
        
        org_metadata = OrgMetadata(
            organization_name=org_data["organization_name"],
            collection_name=org_data["collection_name"],
            admin=AdminInfo(
                admin_id=org_data["admin"]["admin_id"],
                email=org_data["admin"]["email"]
            ),
            created_at=org_data["created_at"]
        )
        
        return OrgCreateResponse(
            message="Organization created successfully",
            organization=org_metadata
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create organization: {str(e)}"
        )


@router.get("/get", response_model=OrgGetResponse, status_code=status.HTTP_200_OK)
async def get_organization(organization_name: str):
    try:
        org_data = await OrgService.get_organization(organization_name)
        
        org_metadata = OrgMetadata(
            organization_name=org_data["organization_name"],
            collection_name=org_data["collection_name"],
            admin=AdminInfo(
                admin_id=org_data["admin"]["admin_id"],
                email=org_data["admin"]["email"]
            ),
            created_at=org_data["created_at"]
        )
        
        return OrgGetResponse(organization=org_metadata)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get organization: {str(e)}"
        )


@router.put("/update", response_model=OrgUpdateResponse, status_code=status.HTTP_200_OK)
async def update_organization(
    request: OrgUpdateRequest,
    admin_payload: dict = Depends(get_current_admin)
):
    try:
        verify_org_access(request.organization_name, admin_payload)
        
        org_data = await OrgService.update_organization(
            request.organization_name,
            request.new_organization_name,
            request.email,
            request.password
        )
        
        org_metadata = OrgMetadata(
            organization_name=org_data["organization_name"],
            collection_name=org_data["collection_name"],
            admin=AdminInfo(
                admin_id=org_data["admin"]["admin_id"],
                email=org_data["admin"]["email"]
            ),
            created_at=org_data["created_at"]
        )
        
        return OrgUpdateResponse(
            message="Organization updated successfully",
            organization=org_metadata
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update organization: {str(e)}"
        )


@router.delete("/delete", response_model=OrgDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_organization(
    request: OrgDeleteRequest,
    admin_payload: dict = Depends(get_current_admin)
):
    try:
        verify_org_access(request.organization_name, admin_payload)
        
        deleted = await OrgService.delete_organization(request.organization_name)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        return OrgDeleteResponse(
            message=f"Organization '{request.organization_name}' deleted successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete organization: {str(e)}"
        )

