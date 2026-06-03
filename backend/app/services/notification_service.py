from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import EmailInvite


async def queue_invite(
    session: AsyncSession,
    tenant_id: int | None,
    survey_id: int,
    recipient_email: str,
    invite_url: str,
) -> EmailInvite:
    invite = EmailInvite(
        tenant_id=tenant_id,
        survey_id=survey_id,
        recipient_email=recipient_email.strip().lower(),
        invite_url=invite_url,
        status="queued",
    )
    session.add(invite)
    return invite


async def mark_invites_sent(session: AsyncSession, invites: list[EmailInvite]) -> None:
    for invite in invites:
        invite.status = "sent"
        invite.sent_at = datetime.now(timezone.utc)
