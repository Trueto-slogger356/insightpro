from fastapi import HTTPException, status

from app.models.user import User


ROLE_PERMISSIONS = {
    "super_admin": {"*"},
    "customer_admin": {"tenant:read", "tenant:write", "survey:write", "analytics:read", "invite:write", "export:read", "audit:read"},
    "analyst": {"tenant:read", "analytics:read", "export:read"},
}


def require_permission(user: User, permission: str) -> None:
    permissions = ROLE_PERMISSIONS.get(user.role, set())
    if "*" in permissions or permission in permissions:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role permissions")


def enforce_tenant(user: User, tenant_id: int | None) -> None:
    if user.role == "super_admin":
        return
    if user.tenant_id and tenant_id == user.tenant_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant data access denied")
