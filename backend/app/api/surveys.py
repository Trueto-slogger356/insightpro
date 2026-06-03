from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.response import SurveyResponse
from app.models.survey import Question, Survey
from app.models.user import User
from app.schemas.survey import SurveyCreate, SurveyListItem, SurveyRead
from app.services.audit_service import write_audit
from app.services.export_service import responses_to_csv, responses_to_excel_xml, responses_to_pdf_html
from app.services.permissions import enforce_tenant, require_permission


router = APIRouter(prefix="/surveys", tags=["surveys"])


@router.get("", response_model=list[SurveyListItem])
async def list_surveys(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> list[SurveyListItem]:
    require_permission(_, "analytics:read")
    result = await session.execute(
        select(Survey, func.count(SurveyResponse.id).label("response_count"))
        .outerjoin(SurveyResponse, SurveyResponse.survey_id == Survey.id)
        .where(True if _.role == "super_admin" else Survey.tenant_id == _.tenant_id)
        .group_by(Survey.id)
        .order_by(Survey.created_at.desc())
    )
    return [
        SurveyListItem(
            id=survey.id,
            title=survey.title,
            status=survey.status,
            public_slug=survey.public_slug,
            custom_url=survey.custom_url,
            response_mode=survey.response_mode,
            created_at=survey.created_at,
            response_count=response_count,
        )
        for survey, response_count in result.all()
    ]


@router.post("", response_model=SurveyRead, status_code=status.HTTP_201_CREATED)
async def create_survey(
    payload: SurveyCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Survey:
    require_permission(user, "survey:write")
    survey = Survey(
        tenant_id=user.tenant_id,
        title=payload.title,
        description=payload.description,
        public_slug=uuid4().hex[:12],
        custom_url=payload.custom_url.strip().lower() if payload.custom_url else None,
        response_mode=payload.response_mode,
        brand_logo_url=payload.brand_logo_url,
        brand_primary_color=payload.brand_primary_color,
        brand_theme=payload.brand_theme,
        default_country=payload.default_country,
        default_product=payload.default_product,
        default_service=payload.default_service,
        default_region=payload.default_region,
        created_by_id=user.id,
    )
    session.add(survey)
    await session.flush()

    for index, question_payload in enumerate(payload.questions, start=1):
        question = Question(
            survey_id=survey.id,
            position=index,
            code=question_payload.code,
            prompt=question_payload.prompt,
            question_type=question_payload.question_type,
            required=question_payload.required,
            options=question_payload.options,
            branch_rules=[rule.model_dump() for rule in question_payload.branch_rules or []],
            display_conditions=[rule.model_dump() for rule in question_payload.display_conditions or []],
            scoring_rules=question_payload.scoring_rules,
        )
        session.add(question)

    await write_audit(session, user, "survey.created", "survey", survey.id, {"title": survey.title})
    await session.commit()
    result = await session.execute(
        select(Survey).options(selectinload(Survey.questions)).where(Survey.id == survey.id)
    )
    return result.scalar_one()


@router.get("/{survey_id}", response_model=SurveyRead)
async def get_survey(
    survey_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Survey:
    result = await session.execute(
        select(Survey).options(selectinload(Survey.questions)).where(Survey.id == survey_id)
    )
    survey = result.scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey not found")
    enforce_tenant(_, survey.tenant_id)
    return survey


@router.post("/{survey_id}/publish", response_model=SurveyRead)
async def publish_survey(
    survey_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Survey:
    result = await session.execute(
        select(Survey).options(selectinload(Survey.questions)).where(Survey.id == survey_id)
    )
    survey = result.scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey not found")
    require_permission(_, "survey:write")
    enforce_tenant(_, survey.tenant_id)
    survey.status = "published"
    await write_audit(session, _, "survey.published", "survey", survey.id, {"public_slug": survey.public_slug})
    await session.commit()
    await session.refresh(survey)
    return survey


@router.get("/{survey_id}/responses", response_model=list[dict])
async def list_responses(
    survey_id: int,
    country: str | None = None,
    product: str | None = None,
    service: str | None = None,
    region: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> list[dict]:
    require_permission(_, "analytics:read")
    survey = await session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey not found")
    enforce_tenant(_, survey.tenant_id)
    statement = select(SurveyResponse).where(SurveyResponse.survey_id == survey_id)
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
    result = await session.execute(
        statement.order_by(SurveyResponse.submitted_at.desc())
    )
    return [
        {
            "id": row.id,
            "respondent_key": row.respondent_key,
            "respondent_email": row.respondent_email,
            "status": row.status,
            "answers": row.answers,
            "score": row.score,
            "country": row.country,
            "product": row.product,
            "service": row.service,
            "region": row.region,
            "submitted_at": row.submitted_at,
        }
        for row in result.scalars().all()
    ]


@router.get("/{survey_id}/responses/export")
async def export_responses(
    survey_id: int,
    format: str = "csv",
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Response:
    require_permission(_, "export:read")
    survey = await session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey not found")
    enforce_tenant(_, survey.tenant_id)
    result = await session.execute(
        select(SurveyResponse)
        .where(SurveyResponse.survey_id == survey_id)
        .order_by(SurveyResponse.submitted_at.asc())
    )
    rows = list(result.scalars().all())
    if format == "xlsx":
        body = responses_to_excel_xml(rows)
        media_type = "application/vnd.ms-excel"
        filename = f"survey-{survey_id}-responses.xls"
    elif format == "pdf":
        body = responses_to_pdf_html(rows)
        media_type = "text/html"
        filename = f"survey-{survey_id}-responses.html"
    else:
        body = responses_to_csv(rows)
        media_type = "text/csv"
        filename = f"survey-{survey_id}-responses.csv"
    return Response(
        content=body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
