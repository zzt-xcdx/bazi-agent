from __future__ import annotations

from datetime import datetime
from typing import Dict, Literal, Optional

from pydantic import BaseModel, Field


Gender = Literal["male", "female", "other"]
CalendarType = Literal["solar", "lunar"]


class BaziRequest(BaseModel):
    name: str = Field(..., description="姓名")
    gender: Gender = Field(..., description="性别")
    birth_datetime: datetime = Field(
        ..., description="出生时间（本地时间，ISO 格式，如 1995-08-01T10:30:00）"
    )
    calendar: CalendarType = Field(
        "solar", description="历法：solar 阳历 / lunar 农历"
    )
    birth_place: Optional[str] = Field(None, description="出生地（城市即可）")
    question: Optional[str] = Field(
        None, description="如果有特别想问的问题（事业/感情/健康等）"
    )


class Pillar(BaseModel):
    heavenly_stem: str = Field(..., description="天干")
    earthly_branch: str = Field(..., description="地支")
    element: Optional[str] = Field(None, description="五行（木火土金水）")
    ten_god: Optional[str] = Field(None, description="十神（可选）")


class BaziData(BaseModel):
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar
    five_elements_balance: Optional[Dict[str, int]] = Field(
        None, description="五行数量统计"
    )


class BaziAnalysis(BaseModel):
    overview: str
    career: str
    relationship: str
    health: str
    luck_cycles: str


class BaziResponse(BaseModel):
    chart_id: Optional[int] = Field(None, description="本次排盘对应的命盘 ID（数据库主键）")
    bazi: BaziData
    analysis: BaziAnalysis