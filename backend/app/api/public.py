from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.models.response import SurveyResponse
from app.models.survey import Survey
from app.schemas.response import AnswerSaveRequest, ProgressResponse, PublicSurveyResponse, SubmitResponseRequest
from app.services.logic_engine import calculate_score, next_question_code
from app.services.resume_session import ResumeSessionService


router = APIRouter(prefix="/public/surveys", tags=["public surveys"])
resume_service = ResumeSessionService()


async def _load_published_survey(slug: str, session: AsyncSession) -> Survey:
    result = await session.execute(
        select(Survey)
        .options(selectinload(Survey.questions))
        .where((Survey.public_slug == slug) | (Survey.custom_url == slug), Survey.status == "published")
    )
    survey = result.scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Published survey not found")
    return survey


@router.get("/{slug}", response_model=PublicSurveyResponse)
async def open_public_survey(
    slug: str,
    respondent_key: str | None = None,
    email: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> PublicSurveyResponse:
    survey = await _load_published_survey(slug, session)
    key = respondent_key or uuid4().hex
    progress = await resume_service.get(slug, key)
    if not progress:
        progress = {
            "respondent_key": key,
            "answers": {},
            "respondent_email": email,
            "current_question_code": survey.questions[0].code if survey.questions else None,
            "completed": False,
        }
        await resume_service.save(slug, key, progress)

    return PublicSurveyResponse(survey=survey, progress=ProgressResponse(**progress))


@router.post("/{slug}/answers", response_model=ProgressResponse)
async def save_answer(
    slug: str,
    payload: AnswerSaveRequest,
    session: AsyncSession = Depends(get_session),
) -> ProgressResponse:
    survey = await _load_published_survey(slug, session)
    question = next((item for item in survey.questions if item.code == payload.question_code), None)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    answers = (await resume_service.get(slug, payload.respondent_key) or {}).get("answers", {})
    answers[payload.question_code] = payload.answer
    respondent_email = payload.respondent_email or (await resume_service.get(slug, payload.respondent_key) or {}).get("respondent_email")
    current_question_code = next_question_code(survey.questions, payload.question_code, payload.answer)
    progress = {
        "respondent_key": payload.respondent_key,
        "respondent_email": respondent_email,
        "answers": answers,
        "current_question_code": current_question_code,
        "completed": current_question_code is None,
    }
    await resume_service.save(slug, payload.respondent_key, progress)
    return ProgressResponse(**progress)


@router.post("/{slug}/submit", response_model=dict)
async def submit_response(
    slug: str,
    payload: SubmitResponseRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    survey = await _load_published_survey(slug, session)
    progress = await resume_service.get(slug, payload.respondent_key)
    if not progress or not progress.get("answers"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No saved answers found")

    response = SurveyResponse(
        tenant_id=survey.tenant_id,
        survey_id=survey.id,
        respondent_key=payload.respondent_key,
        respondent_email=payload.respondent_email or progress.get("respondent_email"),
        answers=progress["answers"],
        score=calculate_score(survey.questions, progress["answers"]),
        country=payload.country or survey.default_country,
        product=payload.product or survey.default_product,
        service=payload.service or survey.default_service,
        region=payload.region or survey.default_region,
        metadata_json={"response_mode": survey.response_mode},
    )
    session.add(response)
    await session.commit()
    await resume_service.clear(slug, payload.respondent_key)
    return {"response_id": response.id, "status": "submitted"}
