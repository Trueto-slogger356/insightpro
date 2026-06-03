from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


QuestionType = Literal["text", "radio", "checkbox", "dropdown", "rating", "nps"]


class BranchRule(BaseModel):
    answer: Any
    go_to_code: str

    @field_validator("go_to_code")
    @classmethod
    def clean_target_code(cls, value: str) -> str:
        return value.strip()


class QuestionCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    prompt: str = Field(min_length=1)
    question_type: QuestionType
    required: bool = True
    options: list[str] | None = None
    branch_rules: list[BranchRule] | None = None
    display_conditions: list[BranchRule] | None = None
    scoring_rules: dict[str, Any] | None = None

    @field_validator("code", "prompt")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("options", mode="before")
    @classmethod
    def normalize_options(cls, value: Any) -> list[str] | None:
        if value is None:
            return None
        if isinstance(value, str):
            parts = value.replace("\n", ",").split(",")
            return [part.strip() for part in parts if part.strip()]
        if isinstance(value, list):
            return [str(part).strip() for part in value if str(part).strip()]
        return value

    @model_validator(mode="after")
    def validate_options_for_type(self) -> "QuestionCreate":
        choice_types = {"radio", "checkbox", "dropdown"}
        if self.question_type in choice_types and len(self.options or []) < 2:
            raise ValueError("Radio, checkbox, and dropdown questions need at least two options")
        if self.question_type not in choice_types:
            self.options = None
        self.branch_rules = [rule for rule in self.branch_rules or [] if rule.go_to_code]
        self.display_conditions = [rule for rule in self.display_conditions or [] if rule.go_to_code]
        return self


class SurveyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    custom_url: str | None = None
    response_mode: Literal["anonymous", "identified"] = "anonymous"
    brand_logo_url: str | None = None
    brand_primary_color: str = "#126b5f"
    brand_theme: str = "light"
    default_country: str | None = None
    default_product: str | None = None
    default_service: str | None = None
    default_region: str | None = None
    questions: list[QuestionCreate] = Field(min_length=1)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return value.strip()


class QuestionRead(BaseModel):
    id: int
    position: int
    code: str
    prompt: str
    question_type: QuestionType
    required: bool = True
    options: list[str] | None = None
    branch_rules: list[BranchRule] | None = None
    display_conditions: list[BranchRule] | None = None
    scoring_rules: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class SurveyRead(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    public_slug: str
    custom_url: str | None = None
    response_mode: str = "anonymous"
    brand_logo_url: str | None = None
    brand_primary_color: str = "#126b5f"
    brand_theme: str = "light"
    default_country: str | None = None
    default_product: str | None = None
    default_service: str | None = None
    default_region: str | None = None
    created_at: datetime
    questions: list[QuestionRead]

    model_config = {"from_attributes": True}


class SurveyListItem(BaseModel):
    id: int
    title: str
    status: str
    public_slug: str
    custom_url: str | None = None
    response_mode: str = "anonymous"
    created_at: datetime
    response_count: int = 0

    model_config = {"from_attributes": True}
