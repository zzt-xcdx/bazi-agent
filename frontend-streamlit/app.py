import os
from datetime import datetime, time

import requests
import streamlit as st
from dateutil import tz


BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


def main():
    st.set_page_config(page_title="赛博算命 · 八字排盘", page_icon="🔮", layout="centered")

    st.title("🔮 赛博算命 · 四柱八字排盘")
    st.caption("后端：FastAPI + LangChain + DeepSeek · 前端：Streamlit")

    st.header("1. 基本信息")

    with st.form("bazi-form"):
        name = st.text_input("姓名", value="")
        gender = st.selectbox(
            "性别",
            options=["male", "female", "other"],
            format_func=lambda x: {"male": "男", "female": "女", "other": "其他"}[x],
        )

        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("出生日期", value=datetime(1995, 1, 1).date())
        with col2:
            t = st.time_input("出生时间", value=time(8, 0))

        calendar = st.selectbox(
            "历法",
            options=["solar", "lunar"],
            format_func=lambda x: "阳历" if x == "solar" else "农历",
        )

        birth_place = st.text_input("出生地（城市即可）", value="")
        question = st.text_area(
            "有特别想问的问题吗？（选填，例如：事业方向、感情、健康等）",
            height=80,
        )

        submitted = st.form_submit_button("开始排盘并分析")

    if submitted:
        if not name:
            st.error("请填写姓名。")
            return

        local_zone = tz.tzlocal()
        dt_local = datetime.combine(date, t).replace(tzinfo=local_zone)
        birth_iso = dt_local.isoformat()

        payload = {
            "name": name,
            "gender": gender,
            "birth_datetime": birth_iso,
            "calendar": calendar,
            "birth_place": birth_place or None,
            "question": question or None,
        }

        with st.spinner("正在向后端请求排盘与分析，请稍候……"):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/bazi/analyze", json=payload, timeout=120
                )
            except Exception as e:
                st.error(f"请求后端失败：{e}")
                return

        if resp.status_code != 200:
            st.error(f"后端返回错误：{resp.status_code} {resp.text}")
            return

        data = resp.json()

        st.header("2. 四柱八字")
        bazi = data["bazi"]

        cols = st.columns(4)
        labels = ["年柱", "月柱", "日柱", "时柱"]
        keys = ["year", "month", "day", "hour"]

        for col, label, key in zip(cols, labels, keys):
            pillar = bazi[key]
            with col:
                st.subheader(label)
                st.write(f"{pillar['heavenly_stem']}{pillar['earthly_branch']}")
                if pillar.get("element"):
                    st.caption(f"五行：{pillar['element']}")

        if bazi.get("five_elements_balance"):
            st.subheader("五行平衡（按天干简单统计）")
            fe = bazi["five_elements_balance"]
            st.write(", ".join(f"{k}: {v}" for k, v in fe.items()))

        st.header("3. 命理分析")
        analysis = data["analysis"]

        st.subheader("整体概览")
        st.write(analysis.get("overview", ""))

        st.subheader("事业与学业")
        st.write(analysis.get("career", ""))

        st.subheader("感情与婚姻")
        st.write(analysis.get("relationship", ""))

        st.subheader("健康与身心")
        st.write(analysis.get("health", ""))

        st.subheader("大运与流年")
        st.write(analysis.get("luck_cycles", ""))


if __name__ == "__main__":
    main()