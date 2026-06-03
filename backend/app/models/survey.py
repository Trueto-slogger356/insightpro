from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Survey(Base):
    __tablename__ = "surveys"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="draft")
    public_slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    custom_url: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True, index=True)
    response_mode: Mapped[str] = mapped_column(String(30), default="anonymous")
    brand_logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    brand_primary_color: Mapped[str] = mapped_column(String(20), default="#126b5f")
    brand_theme: Mapped[str] = mapped_column(String(40), default="light")
    default_country: Mapped[str | None] = mapped_column(String(80), nullable=True)
    default_product: Mapped[str | None] = mapped_column(String(120), nullable=True)
    default_service: Mapped[str | None] = mapped_column(String(120), nullable=True)
    default_region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    questions: Mapped[list["Question"]] = relationship(
        back_populates="survey",
        cascade="all, delete-orphan",
        order_by="Question.position",
    )
    tenant: Mapped["Tenant | None"] = relationship(back_populates="surveys")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    survey_id: Mapped[int] = mapped_column(ForeignKey("surveys.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    code: Mapped[str] = mapped_column(String(50))
    prompt: Mapped[str] = mapped_column(Text)
    question_type: Mapped[str] = mapped_column(String(30))
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    options: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    branch_rules: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    display_conditions: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    scoring_rules: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    survey: Mapped[Survey] = relationship(back_populates="questions")
