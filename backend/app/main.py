from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, update

from app.api import auth, dashboard, notifications, public, surveys, tenants
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.schema import apply_schema_patches
from app.db.session import SessionLocal, engine
from app.models import Survey, SurveyResponse, Tenant, User


async def seed_admin() -> None:
    async with SessionLocal() as session:
        tenant = await session.scalar(select(Tenant).where(Tenant.slug == "default"))
        if not tenant:
            tenant = Tenant(name="Default Customer", slug="default", primary_color="#126b5f", theme="light")
            session.add(tenant)
            await session.flush()
        result = await session.execute(select(User).where(User.email == "admin@insightpro.local"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                tenant_id=tenant.id,
                email="admin@insightpro.local",
                name="InsightPro Super Admin",
                password_hash=hash_password("admin123"),
                role="super_admin",
            )
            session.add(user)
        else:
            user.tenant_id = user.tenant_id or tenant.id
            if user.role == "admin":
                user.role = "super_admin"
        await session.execute(update(Survey).where(Survey.tenant_id.is_(None)).values(tenant_id=tenant.id))
        await session.execute(update(SurveyResponse).where(SurveyResponse.tenant_id.is_(None)).values(tenant_id=tenant.id))
        await session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await apply_schema_patches(engine)
    await seed_admin()
    yield


settings = get_settings()
app = FastAPI(title="InsightPro API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(surveys.router, prefix="/api")
app.include_router(public.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(tenants.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
