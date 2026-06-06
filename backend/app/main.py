from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# 确保在导入 app.db 之前加载 .env
load_dotenv()

from app.db import Base, engine, get_session
from app.models.db_models import Analysis, BaziChart, Compatibility, Person
from app.models.schemas import (
    BaziRequest,
    BaziResponse,
    CompatibilityRequest,
    CompatibilityResponse,
    ChartSummary,    
)
from app.services.bazi_engine import calculate_bazi
from app.services.bazi_chain import analyze_with_llm, analyze_compatibility


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
        relationship_text=analysis.relationship,
        health=analysis.health,
        luck_cycles=analysis.luck_cycles,
        raw_response=None,
        model_name=os.getenv("DEEPSEEK_MODEL"),
    )
    db.add(db_analysis)
    db.commit()

    return BaziResponse(chart_id=chart.id, bazi=bazi, analysis=analysis)


def _chart_to_payload(chart: BaziChart) -> dict:
    return {
        "year_gz": chart.year_gz,
        "month_gz": chart.month_gz,
        "day_gz": chart.day_gz,
        "hour_gz": chart.hour_gz,
        "five_elements_json": chart.five_elements_json or "{}",
    }


@app.post("/api/bazi/compatibility", response_model=CompatibilityResponse)
async def compatibility(
    req: CompatibilityRequest,
    db: Session = Depends(get_session),
) -> CompatibilityResponse:
    chart_a = db.get(BaziChart, req.chart_id_a)
    chart_b = db.get(BaziChart, req.chart_id_b)

    if not chart_a or not chart_b:
        raise HTTPException(status_code=404, detail="指定的命盘不存在")

    result = await run_in_threadpool(
        analyze_compatibility,
        _chart_to_payload(chart_a),
        _chart_to_payload(chart_b),
        req.question,
    )

    compat = Compatibility(
        chart_a_id=chart_a.id,
        chart_b_id=chart_b.id,
        summary=result.split("\n", 1)[0] if result else "",
        detail=result,
        raw_response=result,
        question=req.question,
    )
    db.add(compat)
    db.commit()

    return CompatibilityResponse(
        chart_id_a=chart_a.id,
        chart_id_b=chart_b.id,
        summary=compat.summary,
        detail=compat.detail,
    )


@app.get("/api/bazi/charts", response_model=list[ChartSummary])
async def list_charts(
    limit: int = 50,
    db: Session = Depends(get_session),
) -> list[ChartSummary]:
    q = (
        db.query(
            BaziChart.id.label("chart_id"),
            Person.name.label("name"),
            Person.gender.label("gender"),
            Person.birth_datetime.label("birth_datetime"),
            Person.calendar.label("calendar"),
            BaziChart.created_at.label("created_at"),
            BaziChart.year_gz,
            BaziChart.month_gz,
            BaziChart.day_gz,
            BaziChart.hour_gz,
        )
        .join(Person, Person.id == BaziChart.person_id)
        .order_by(BaziChart.created_at.desc())
        .limit(limit)
    )
    rows = q.all()
    return [ChartSummary(**dict(r._mapping)) for r in rows]


@app.delete("/api/bazi/chart/{chart_id}")
async def delete_chart(chart_id: int, db: Session = Depends(get_session)) -> dict:
    chart = db.get(BaziChart, chart_id)
    if not chart:
        raise HTTPException(status_code=404, detail="命盘不存在")

    # 删除与该命盘关联的合盘记录
    db.query(Compatibility).filter(
        (Compatibility.chart_a_id == chart_id) | (Compatibility.chart_b_id == chart_id)
    ).delete(synchronize_session=False)
    # 删除关联的分析（cascade 已覆盖，但这里显式确保）
    db.query(Analysis).filter(Analysis.chart_id == chart_id).delete(synchronize_session=False)
    db.delete(chart)
    db.commit()
    return {"status": "ok", "deleted_chart_id": chart_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)