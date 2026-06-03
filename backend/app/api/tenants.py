from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import hash_password
from app.db.session import get_session
from app.models.tenant import AuditLog, Tenant
from app.models.user import User
from app.schemas.tenant import AuditLogRead, TenantCreate, TenantRead, TenantUpdateBranding, UserInviteCreate
from app.services.audit_service import write_audit
from app.services.permissions import enforce_tenant, require_permission


router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("", response_model=list[TenantRead])
async def list_tenants(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[Tenant]:
    require_permission(user, "tenant:read")
    statement = select(Tenant).order_by(Tenant.name)
    if user.role != "super_admin":
        statement = statement.where(Tenant.id == user.tenant_id)
    result = await session.execute(statement)
    return list(result.scalars().all())


@router.post("", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: TenantCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Tenant:
    require_permission(user, "tenant:write")
    if user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admins can create tenants")
    tenant = Tenant(
        name=payload.name.strip(),
        slug=payload.slug.strip().lower(),
        logo_url=payload.logo_url,
        primary_color=payload.primary_color,
        theme=payload.theme,
    )
    session.add(tenant)
    await session.flush()
    await write_audit(session, user, "tenant.created", "tenant", tenant.id, {"name": tenant.name})
    await session.commit()
    await session.refresh(tenant)
    return tenant


@router.patch("/{tenant_id}/branding", response_model=TenantRead)
async def update_branding(
    tenant_id: int,
    payload: TenantUpdateBranding,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Tenant:
    require_permission(user, "tenant:write")
    enforce_tenant(user, tenant_id)
    tenant = await session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    tenant.logo_url = payload.logo_url
    tenant.primary_color = payload.primary_color
    tenant.theme = payload.theme
    await write_audit(session, user, "tenant.branding_updated", "tenant", tenant.id, payload.model_dump())
    await session.commit()
    await session.refresh(tenant)
    return tenant


@router.post("/{tenant_id}/users", response_model=dict)
async def create_tenant_user(
    tenant_id: int,
    payload: UserInviteCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> dict:
    require_permission(user, "tenant:write")
    enforce_tenant(user, tenant_id)
    existing = await session.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    password = uuid4().hex[:12]
    new_user = User(
        tenant_id=tenant_id,
        email=payload.email.strip().lower(),
        name=payload.name.strip(),
        role=payload.role,
        password_hash=hash_password(password),
    )
    session.add(new_user)
    await write_audit(session, user, "user.created", "user", payload.email, {"role": payload.role})
    await session.commit()
    return {"email": new_user.email, "temporary_password": password}


@router.get("/{tenant_id}/audit-logs", response_model=list[AuditLogRead])
async def audit_logs(
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[AuditLog]:
    require_permission(user, "audit:read")
    enforce_tenant(user, tenant_id)
    result = await session.execute(
        select(AuditLog).where(AuditLog.tenant_id == tenant_id).order_by(AuditLog.created_at.desc()).limit(100)
    )
    return list(result.scalars().all())
