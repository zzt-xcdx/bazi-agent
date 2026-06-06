import os
from datetime import datetime, time

import requests
import streamlit as st
from dateutil import tz


BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


def load_charts():
    """拉取历史命盘列表"""
    try:
        resp_list = requests.get(f"{BACKEND_URL}/api/bazi/charts", timeout=60)
        if resp_list.status_code == 200:
            return resp_list.json()
        st.warning(f"历史命盘加载失败：{resp_list.status_code} {resp_list.text}")
    except Exception as e:
        st.warning(f"历史命盘加载异常：{e}")
    return []


def main():
    st.set_page_config(page_title="赛博算命 · 八字命理", page_icon="🔮", layout="wide")

    st.title("🔮 赛博算命 · 八字命理")
    st.caption("后端：FastAPI + LangChain + DeepSeek · 前端：Streamlit")

    tab_analyze, tab_history = st.tabs(["排盘与分析", "历史命盘 / 合盘 / 删除"])

    # ---- Tab 1: 排盘与分析 ----
    with tab_analyze:
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

            if not resp or resp.status_code != 200:
                st.error(
                    f"后端返回错误：{resp.status_code if resp else 'N/A'} {resp.text if resp else ''}"
                )
                return

            data = resp.json()

            st.header("2. 四柱八字")
            bazi = data["bazi"]
            chart_id = data.get("chart_id")
            if chart_id:
                st.caption(f"本次命盘 ID：{chart_id}")

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

    # ---- Tab 2: 历史命盘 / 合盘 / 删除 ----
    with tab_history:
        st.header("历史命盘列表")
        charts = load_charts()

        if charts:
            st.dataframe(
                charts,
                column_config={
                    "chart_id": "命盘ID",
                    "name": "姓名",
                    "gender": "性别",
                    "birth_datetime": "出生时间",
                    "calendar": "历法",
                    "created_at": "创建时间",
                    "year_gz": "年柱",
                    "month_gz": "月柱",
                    "day_gz": "日柱",
                    "hour_gz": "时柱",
                },
                hide_index=True,
                height=320,
            )

        st.subheader("合盘 / 检核")
        compat_cols = st.columns(2)
        chart_ids = [c["chart_id"] for c in charts] if charts else []
        names_map = {
            c["chart_id"]: f"{c['chart_id']} | {c['name']} | {c['birth_datetime']}"
            for c in charts
        }

        with st.form("compat-form"):
            with compat_cols[0]:
                chart_id_a = st.selectbox(
                    "命盘 A",
                    options=chart_ids or [1],
                    format_func=lambda x: names_map.get(x, str(x)),
                    index=0 if chart_ids else 0,
                )
            with compat_cols[1]:
                chart_id_b = st.selectbox(
                    "命盘 B",
                    options=chart_ids or [1],
                    format_func=lambda x: names_map.get(x, str(x)),
                    index=1 if chart_ids and len(chart_ids) > 1 else 0,
                )

            compat_question = st.text_area(
                "想问的合盘重点（如：适合结婚/合作/需注意什么）",
                height=80,
            )
            compat_submit = st.form_submit_button("查询两人合盘")

        if compat_submit:
            payload_compat = {
                "chart_id_a": int(chart_id_a),
                "chart_id_b": int(chart_id_b),
                "question": compat_question or None,
            }
            with st.spinner("正在请求合盘分析..."):
                try:
                    resp_compat = requests.post(
                        f"{BACKEND_URL}/api/bazi/compatibility",
                        json=payload_compat,
                        timeout=120,
                    )
                except Exception as e:
                    st.error(f"请求合盘失败：{e}")
                    resp_compat = None

            if resp_compat:
                if resp_compat.status_code != 200:
                    st.error(
                        f"后端合盘接口错误：{resp_compat.status_code} {resp_compat.text}"
                    )
                else:
                    compat = resp_compat.json()
                    st.subheader("合盘结论摘要")
                    st.write(compat.get("summary", ""))
                    st.subheader("合盘详细分析")
                    st.write(compat.get("detail", "（无详细说明）"))

        st.subheader("删除命盘")
        if chart_ids:
            del_chart_id = st.selectbox(
                "选择要删除的命盘",
                options=chart_ids,
                format_func=lambda x: names_map.get(x, str(x)),
                key="delete-chart",
            )
            if st.button("删除选中命盘", type="secondary"):
                with st.spinner("正在删除..."):
                    try:
                        resp_del = requests.delete(
                            f"{BACKEND_URL}/api/bazi/chart/{del_chart_id}", timeout=30
                        )
                        if resp_del.status_code == 200:
                            st.success(f"命盘 {del_chart_id} 已删除，请刷新列表。")
                        else:
                            st.error(
                                f"删除失败：{resp_del.status_code} {resp_del.text}"
                            )
                    except Exception as e:
                        st.error(f"删除请求失败：{e}")


if __name__ == "__main__":
    main()