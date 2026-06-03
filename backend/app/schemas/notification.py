from pydantic import BaseModel, Field


class InviteRequest(BaseModel):
    survey_id: int
    recipient_emails: list[str] = Field(min_length=1)


class InviteRead(BaseModel):
    id: int
    survey_id: int
    recipient_email: str
    status: str
    invite_url: str

    model_config = {"from_attributes": True}
