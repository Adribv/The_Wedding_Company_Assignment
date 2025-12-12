from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Request schemas
class OrgCreateRequest(BaseModel):
    organization_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class OrgGetRequest(BaseModel):
    organization_name: str


class OrgUpdateRequest(BaseModel):
    organization_name: str
    new_organization_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)


class OrgDeleteRequest(BaseModel):
    organization_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Response schemas
class AdminInfo(BaseModel):
    admin_id: str
    email: str


class OrgMetadata(BaseModel):
    organization_name: str
    collection_name: str
    admin: AdminInfo
    created_at: datetime


class OrgCreateResponse(BaseModel):
    message: str
    organization: OrgMetadata


class OrgGetResponse(BaseModel):
    organization: OrgMetadata


class OrgUpdateResponse(BaseModel):
    message: str
    organization: OrgMetadata


class OrgDeleteResponse(BaseModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ErrorResponse(BaseModel):
    detail: str

