from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import analyses, auth, categories, comparisons, alerts, webhooks, payments, admin

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("startup", environment=settings.ENVIRONMENT)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    log.info("shutdown")
    await engine.dispose()


app = FastAPI(
    title="Business Location Intelligence Platform",
    description="Data-backed market opportunity reports for entrepreneurs",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/v1/auth",               tags=["auth"])
app.include_router(analyses.router,    prefix="/v1/analyses",           tags=["analyses"])
app.include_router(categories.router,  prefix="/v1/business-categories", tags=["categories"])
app.include_router(comparisons.router, prefix="/v1/comparisons",        tags=["comparisons"])
app.include_router(alerts.router,      prefix="/v1/alerts",             tags=["alerts"])
app.include_router(payments.router,    prefix="/v1/payments",           tags=["payments"])
app.include_router(admin.router,       prefix="/v1/admin",              tags=["admin"])
app.include_router(webhooks.router,    prefix="/v1/webhooks",           tags=["webhooks"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
