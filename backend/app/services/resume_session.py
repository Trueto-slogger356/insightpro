import json
from typing import Any

from redis.asyncio import Redis

from app.core.config import get_settings


SESSION_TTL_SECONDS = 60 * 60 * 24 * 14


class ResumeSessionService:
    def __init__(self) -> None:
        self.redis = Redis.from_url(get_settings().redis_url, decode_responses=True)

    @staticmethod
    def _key(survey_slug: str, respondent_key: str) -> str:
        return f"survey-progress:{survey_slug}:{respondent_key}"

    async def get(self, survey_slug: str, respondent_key: str) -> dict[str, Any] | None:
        raw = await self.redis.get(self._key(survey_slug, respondent_key))
        return json.loads(raw) if raw else None

    async def save(self, survey_slug: str, respondent_key: str, progress: dict[str, Any]) -> None:
        await self.redis.set(
            self._key(survey_slug, respondent_key),
            json.dumps(progress),
            ex=SESSION_TTL_SECONDS,
        )

    async def clear(self, survey_slug: str, respondent_key: str) -> None:
        await self.redis.delete(self._key(survey_slug, respondent_key))
