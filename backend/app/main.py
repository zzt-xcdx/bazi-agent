from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db import Base, engine, get_session
from app.models.db_models import Person, BaziChart, Analysis
from app.models.schemas import BaziRequest, BaziResponse
from app.services.bazi_engine import calculate_bazi
from app.services.bazi_chain import analyze_with_llm


load_dotenv()

app = FastAPI(title="Bazi Skill API", version="0.1.0")

origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """应用启动时创建数据库表（如果尚不存在）。"""
    Base.metadata.create_all(bind=engine)


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.post("/api/bazi/analyze", response_model=BaziResponse)
async def analyze_bazi(
    req: BaziRequest,
    db: Session = Depends(get_session),
) -> BaziResponse:
    # 1. 排盘（纯计算）
    bazi = calculate_bazi(req)

    # 2. 命理分析（DeepSeek / 占位）
    analysis = await run_in_threadpool(analyze_with_llm, bazi, req)

    # 3. 落库：Person + BaziChart + Analysis
    person = Person(
        name=req.name,
        gender=req.gender,
        birth_datetime=req.birth_datetime,
        calendar=req.calendar,
        birth_place=req.birth_place,
    )
    db.add(person)
    db.flush()  # 先拿到 person.id

    year_gz = f"{bazi.year.heavenly_stem}{bazi.year.earthly_branch}"
    month_gz = f"{bazi.month.heavenly_stem}{bazi.month.earthly_branch}"
    day_gz = f"{bazi.day.heavenly_stem}{bazi.day.earthly_branch}"
    hour_gz = f"{bazi.hour.heavenly_stem}{bazi.hour.earthly_branch}"

    import json

    chart = BaziChart(
        person_id=person.id,
        year_gz=year_gz,
        month_gz=month_gz,
        day_gz=day_gz,
        hour_gz=hour_gz,
        five_elements_json=json.dumps(bazi.five_elements_balance or {}, ensure_ascii=False),
    )
    db.add(chart)
    db.flush()

    db_analysis = Analysis(
        chart_id=chart.id,
        overview=analysis.overview,
        career=analysis.career,
        relationship=analysis.relationship,
        health=analysis.health,
        luck_cycles=analysis.luck_cycles,
        raw_response=None,
        model_name=os.getenv("DEEPSEEK_MODEL"),
    )
    db.add(db_analysis)
    db.commit()

    return BaziResponse(chart_id=chart.id, bazi=bazi, analysis=analysis)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)