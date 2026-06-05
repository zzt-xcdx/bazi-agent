from __future__ import annotations

import json
import os
from typing import Any, Dict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.models.schemas import BaziAnalysis, BaziData, BaziRequest


def get_llm() -> ChatOpenAI:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY 未配置，请在 .env 或环境变量中设置。")

    base_url = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0.7,
    )


def _build_prompt(bazi: BaziData, req: BaziRequest) -> str:
    data: Dict[str, Any] = {
        "name": req.name,
        "gender": req.gender,
        "birth_datetime": req.birth_datetime.isoformat(),
        "calendar": req.calendar,
        "birth_place": req.birth_place,
        "question": req.question,
        "bazi": {
            "year": bazi.year.model_dump(),
            "month": bazi.month.model_dump(),
            "day": bazi.day.model_dump(),
            "hour": bazi.hour.model_dump(),
            "five_elements_balance": bazi.five_elements_balance,
        },
    }

    instructions = f"""
你是一名专业的四柱八字命理师，参考《穷通宝鉴》《三命通会》《滴天髓》《子平真诠》等经典。

下面是客户的基本信息和排出的四柱八字（JSON）：

{json.dumps(data, ensure_ascii=False, indent=2)}

请你基于上面的信息进行系统分析，并严格按以下 JSON 结构输出（不要出现多余文字，不要带语言标记，不要解释）：

{{
  "overview": "整体命局概览，说明日主强弱、格局、用神、大致性格与人生基调，300~600 字左右。",
  "career": "事业与学业分析，适合的方向、职场风格、关键运势阶段，200~400 字。",
  "relationship": "感情与婚姻分析，感情态度、婚缘时间、需注意的问题，200~400 字。",
  "health": "健康与身心状况，容易出现问题的部位或阶段，生活调养建议，150~300 字。",
  "luck_cycles": "大运与流年简要提示，指出几个关键年份或阶段的主题与建议，200~400 字。"
}}

要求：
- 结合日主强弱、十神、格局和五行平衡做分析。
- 不要使用“绝对肯定”的语言，使用“倾向于、更适合、有可能”等。
- 所有内容使用简体中文。
- 严格输出 JSON，键名必须是 overview/career/relationship/health/luck_cycles。
"""
    return instructions.strip()


def analyze_with_llm(bazi: BaziData, req: BaziRequest) -> BaziAnalysis:
    # 如果还没配置 DEEPSEEK_API_KEY，则返回一个占位分析，避免直接报 500
    if not os.getenv("DEEPSEEK_API_KEY"):
        return BaziAnalysis(
            overview="后端尚未配置 DEEPSEEK_API_KEY，当前仅展示基础四柱排盘结果。请在 backend/.env 中配置 DeepSeek API Key 后重启服务，即可启用 AI 命理分析。",
            career="（未启用 DeepSeek，暂不提供详细事业分析。）",
            relationship="（未启用 DeepSeek，暂不提供详细感情分析。）",
            health="（未启用 DeepSeek，暂不提供详细健康分析。）",
            luck_cycles="（未启用 DeepSeek，暂不提供详细大运流年分析。）",
        )

    llm = get_llm()
    prompt = _build_prompt(bazi, req)

    messages = [
        SystemMessage(
            content="你是一名专业严谨、重视实证的中国传统命理师，擅长结合四柱八字给出中肯建议。"
        ),
        HumanMessage(content=prompt),
    ]

    resp = llm.invoke(messages)
    text = resp.content

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return BaziAnalysis(
            overview=text,
            career="模型未按预期返回 JSON，已将完整内容放在 overview 字段。",
            relationship="",
            health="",
            luck_cycles="",
        )

    return BaziAnalysis(
        overview=data.get("overview", ""),
        career=data.get("career", ""),
        relationship=data.get("relationship", ""),
        health=data.get("health", ""),
        luck_cycles=data.get("luck_cycles", ""),
    )