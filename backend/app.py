from __future__ import annotations

from fastapi import FastAPI

from backend.api.candidate import router as candidate_router
from backend.api.job_description import router as job_description_router
from backend.api.match import router as match_router
from backend.api.upload import router as upload_router
from backend.config.config import AppConfig
from backend.repositories.candidate_repo import init_candidate_db
from backend.repositories.jd_repo import init_jd_db
from backend.utils.logger import configure_logging

config = AppConfig()
configure_logging(config=config)

app = FastAPI(title="Hiring Intelligence Platform", version="0.1.0")
app.include_router(upload_router)
app.include_router(candidate_router)
app.include_router(job_description_router)
app.include_router(match_router)


@app.on_event("startup")
async def on_startup() -> None:
    config.ensure_directories()
    init_candidate_db(db_path=str(config.sqlite_db_path))
    init_jd_db(db_path=str(config.sqlite_db_path))


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "database": str(config.sqlite_db_path)}
