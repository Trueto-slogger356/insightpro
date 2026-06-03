from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.response import SurveyResponse
from app.models.survey import Survey
from app.models.user import User


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def dashboard_summary(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    survey_filter = True if _.role == "super_admin" else Survey.tenant_id == _.tenant_id
    response_filter = True if _.role == "super_admin" else SurveyResponse.tenant_id == _.tenant_id
    survey_count = await session.scalar(select(func.count(Survey.id)).where(survey_filter))
    published_count = await session.scalar(select(func.count(Survey.id)).where(Survey.status == "published", survey_filter))
    response_count = await session.scalar(select(func.count(SurveyResponse.id)).where(response_filter))
    latest = await session.execute(select(Survey).where(survey_filter).order_by(Survey.created_at.desc()).limit(5))
    return {
        "surveys": survey_count or 0,
        "published": published_count or 0,
        "responses": response_count or 0,
        "latest_surveys": [
            {"id": survey.id, "title": survey.title, "status": survey.status, "public_slug": survey.public_slug}
            for survey in latest.scalars().all()
        ],
    }


@router.get("/analytics")
async def analytics(
    survey_id: int | None = None,
    country: str | None = None,
    product: str | None = None,
    service: str | None = None,
    region: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    statement = select(SurveyResponse)
    if _.role != "super_admin":
        statement = statement.where(SurveyResponse.tenant_id == _.tenant_id)
    if survey_id:
        statement = statement.where(SurveyResponse.survey_id == survey_id)
    if country:
        statement = statement.where(SurveyResponse.country == country)
    if product:
        statement = statement.where(SurveyResponse.product == product)
    if service:
        statement = statement.where(SurveyResponse.service == service)
    if region:
        statement = statement.where(SurveyResponse.region == region)
    if date_from:
        statement = statement.where(SurveyResponse.submitted_at >= date_from)
    if date_to:
        statement = statement.where(SurveyResponse.submitted_at <= date_to)
    rows = list((await session.execute(statement)).scalars().all())
    by_region: dict[str, int] = {}
    by_product: dict[str, int] = {}
    by_score: dict[str, int] = {"promoters": 0, "passives": 0, "detractors": 0}
    for row in rows:
        by_region[row.region or "Unassigned"] = by_region.get(row.region or "Unassigned", 0) + 1
        by_product[row.product or "Unassigned"] = by_product.get(row.product or "Unassigned", 0) + 1
        if row.score is not None:
            if row.score >= 9:
                by_score["promoters"] += 1
            elif row.score >= 7:
                by_score["passives"] += 1
            else:
                by_score["detractors"] += 1
    average_score = round(sum(row.score or 0 for row in rows) / len(rows), 2) if rows else 0
    return {
        "responses": len(rows),
        "average_score": average_score,
        "by_region": by_region,
        "by_product": by_product,
        "sentiment_buckets": by_score,
    }
