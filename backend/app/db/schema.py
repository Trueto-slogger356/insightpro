from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


SCHEMA_PATCHES = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS tenant_id INTEGER",
    "ALTER TABLE surveys ADD COLUMN IF NOT EXISTS tenant_id INTEGER",
    "ALTER TABLE surveys ADD COLUMN IF NOT EXISTS custom_url VARCHAR(120)",
    "ALTER TABLE surveys ADD COLUMN IF NOT EXISTS response_mode VARCHAR(30) DEFAULT 'anonymous'",
    "ALTER TABLE surveys ADD COLUMN IF NOT EXISTS brand_logo_url VARCHAR(500)",
    "ALTER TABLE surveys ADD COLUMN IF NOT EXISTS brand_primary_color VARCHAR(20) DEFAULT '#126b5f'",
    "ALTER TABLE surveys ADD COLUMN IF NOT EXISTS brand_theme VARCHAR(40) DEFAULT 'light'",
    "ALTER TABLE surveys ADD COLUMN IF NOT EXISTS default_country VARCHAR(80)",
    "ALTER TABLE surveys ADD COLUMN IF NOT EXISTS default_product VARCHAR(120)",
    "ALTER TABLE surveys ADD COLUMN IF NOT EXISTS default_service VARCHAR(120)",
    "ALTER TABLE surveys ADD COLUMN IF NOT EXISTS default_region VARCHAR(120)",
    "ALTER TABLE questions ADD COLUMN IF NOT EXISTS display_conditions JSON",
    "ALTER TABLE questions ADD COLUMN IF NOT EXISTS scoring_rules JSON",
    "ALTER TABLE survey_responses ADD COLUMN IF NOT EXISTS tenant_id INTEGER",
    "ALTER TABLE survey_responses ADD COLUMN IF NOT EXISTS respondent_email VARCHAR(255)",
    "ALTER TABLE survey_responses ADD COLUMN IF NOT EXISTS score INTEGER",
    "ALTER TABLE survey_responses ADD COLUMN IF NOT EXISTS country VARCHAR(80)",
    "ALTER TABLE survey_responses ADD COLUMN IF NOT EXISTS product VARCHAR(120)",
    "ALTER TABLE survey_responses ADD COLUMN IF NOT EXISTS service VARCHAR(120)",
    "ALTER TABLE survey_responses ADD COLUMN IF NOT EXISTS region VARCHAR(120)",
    "ALTER TABLE survey_responses ADD COLUMN IF NOT EXISTS metadata_json JSON",
    "CREATE INDEX IF NOT EXISTS ix_users_tenant_id ON users (tenant_id)",
    "CREATE INDEX IF NOT EXISTS ix_surveys_tenant_id ON surveys (tenant_id)",
    "CREATE INDEX IF NOT EXISTS ix_surveys_custom_url ON surveys (custom_url)",
    "CREATE INDEX IF NOT EXISTS ix_survey_responses_tenant_id ON survey_responses (tenant_id)",
    "CREATE INDEX IF NOT EXISTS ix_survey_responses_country ON survey_responses (country)",
    "CREATE INDEX IF NOT EXISTS ix_survey_responses_product ON survey_responses (product)",
    "CREATE INDEX IF NOT EXISTS ix_survey_responses_service ON survey_responses (service)",
    "CREATE INDEX IF NOT EXISTS ix_survey_responses_region ON survey_responses (region)",
]


async def apply_schema_patches(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        for statement in SCHEMA_PATCHES:
            await conn.execute(text(statement))
