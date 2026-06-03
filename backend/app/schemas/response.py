from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.survey import SurveyRead


class AnswerSaveRequest(BaseModel):
    respondent_key: str = Field(min_length=8)
    question_code: str
    answer: Any
    respondent_email: str | None = None


class SubmitResponseRequest(BaseModel):
    respondent_key: str = Field(min_length=8)
    respondent_email: str | None = None
    country: str | None = None
    product: str | None = None
    service: str | None = None
    region: str | None = None


class ProgressResponse(BaseModel):
    respondent_key: str
    answers: dict[str, Any]
    current_question_code: str | None
    completed: bool = False


class PublicSurveyResponse(BaseModel):
    survey: SurveyRead
    progress: ProgressResponse


class ResponseRead(BaseModel):
    id: int
    survey_id: int
    respondent_key: str
    respondent_email: str | None = None
    status: str
    answers: dict[str, Any]
    score: int | None = None
    country: str | None = None
    product: str | None = None
    service: str | None = None
    region: str | None = None
    submitted_at: datetime

    model_config = {"from_attributes": True}
