from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import AuditLog
from app.models.user import User


async def write_audit(
    session: AsyncSession,
    user: User | None,
    action: str,
    entity_type: str,
    entity_id: str | int | None = None,
    detail: dict | None = None,
) -> None:
    session.add(
        AuditLog(
            tenant_id=user.tenant_id if user else None,
            actor_user_id=user.id if user else None,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            detail=detail,
        )
    )
