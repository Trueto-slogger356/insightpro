from datetime import datetime

from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    slug: str = Field(min_length=2, max_length=80)
    logo_url: str | None = None
    primary_color: str = "#126b5f"
    theme: str = "light"


class TenantRead(BaseModel):
    id: int
    name: str
    slug: str
    logo_url: str | None
    primary_color: str
    theme: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantUpdateBranding(BaseModel):
    logo_url: str | None = None
    primary_color: str = "#126b5f"
    theme: str = "light"


class UserInviteCreate(BaseModel):
    email: str
    name: str
    role: str = "analyst"


class AuditLogRead(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: str | None
    detail: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
