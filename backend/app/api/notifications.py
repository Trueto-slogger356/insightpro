from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.survey import Survey
from app.models.tenant import EmailInvite
from app.models.user import User
from app.schemas.notification import InviteRead, InviteRequest
from app.services.audit_service import write_audit
from app.services.notification_service import mark_invites_sent, queue_invite
from app.services.permissions import enforce_tenant, require_permission


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/invites", response_model=list[InviteRead], status_code=status.HTTP_201_CREATED)
async def send_invites(
    payload: InviteRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[EmailInvite]:
    require_permission(user, "invite:write")
    survey = await session.get(Survey, payload.survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey not found")
    enforce_tenant(user, survey.tenant_id)
    base_url = str(request.base_url).rstrip("/").replace(":8000", ":5173")
    public_path = survey.custom_url or survey.public_slug
    invites = []
    for email in payload.recipient_emails:
        invite_url = f"{base_url}/survey/{public_path}?email={email.strip().lower()}"
        invites.append(await queue_invite(session, survey.tenant_id, survey.id, email, invite_url))
    await mark_invites_sent(session, invites)
    await write_audit(session, user, "invite.sent", "survey", survey.id, {"count": len(invites)})
    await session.commit()
    return invites


@router.get("/invites", response_model=list[InviteRead])
async def list_invites(
    survey_id: int | None = None,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[EmailInvite]:
    require_permission(user, "invite:write")
    statement = select(EmailInvite).order_by(EmailInvite.created_at.desc()).limit(100)
    if user.role != "super_admin":
        statement = statement.where(EmailInvite.tenant_id == user.tenant_id)
    if survey_id:
        statement = statement.where(EmailInvite.survey_id == survey_id)
    result = await session.execute(statement)
    return list(result.scalars().all())
