from __future__ import annotations

from datetime import datetime
from typing import Dict

from lunar_python import Lunar, Solar

from app.models.schemas import BaziData, Pillar, BaziRequest


STEM_ELEMENT_MAP: Dict[str, str] = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
}


def _split_ganzhi(gz: str) -> tuple[str, str]:
    """把 “甲子” 这种格式拆成 (天干, 地支)。"""
    if len(gz) >= 2:
        return gz[0], gz[1:]
    if len(gz) == 1:
        return gz, ""
    return "", ""


def _pillar_from_ganzhi(gz: str) -> Pillar:
    stem, branch = _split_ganzhi(gz)
    element = STEM_ELEMENT_MAP.get(stem)
    return Pillar(
        heavenly_stem=stem,
        earthly_branch=branch,
        element=element,
        ten_god=None,
    )


def _calc_five_elements_balance(
    year: Pillar, month: Pillar, day: Pillar, hour: Pillar
) -> Dict[str, int]:
    counter = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for p in (year, month, day, hour):
        if p.element in counter:
            counter[p.element] += 1
    return {k: v for k, v in counter.items() if v > 0}


def calculate_bazi(req: BaziRequest) -> BaziData:
    """
    根据出生时间计算四柱八字。
    - calendar=solar：视为阳历，先转农历再排盘
    - calendar=lunar：视为农历日期
    """
    dt: datetime = req.birth_datetime

    if req.calendar == "solar":
        solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        lunar = solar.getLunar()
    else:
        lunar = Lunar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    # lunar-python 1.4.x API：使用 getXXXInGanZhi 获取干支
    year_gz = lunar.getYearInGanZhi()
    month_gz = lunar.getMonthInGanZhi()
    day_gz = lunar.getDayInGanZhi()
    time_gz = lunar.getTimeInGanZhi()

    year_pillar = _pillar_from_ganzhi(year_gz)
    month_pillar = _pillar_from_ganzhi(month_gz)
    day_pillar = _pillar_from_ganzhi(day_gz)
    hour_pillar = _pillar_from_ganzhi(time_gz)

    five_elements_balance = _calc_five_elements_balance(
        year_pillar, month_pillar, day_pillar, hour_pillar
    )

    return BaziData(
        year=year_pillar,
        month=month_pillar,
        day=day_pillar,
        hour=hour_pillar,
        five_elements_balance=five_elements_balance,
    )