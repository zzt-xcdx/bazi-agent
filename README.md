<div align="center">

# 🔮 命理项目 - AI 四柱八字分析系统

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red?logo=streamlit)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**基于 LLM 的智能命理分析 Agent | 为了找 AI Agent 实习，反向学习一波 🚀**

</div>

## 📋 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python + FastAPI + LangChain + DeepSeek API |
| **前端** | Streamlit |
| **数据库** | (SQLite/PostgreSQL) |

## ✨ 功能特性

- [x] 🎯 根据出生信息排四柱八字（年、月、日、时）
- [x] 🤖 调用 kimi 进行智能命理分析（事业 / 感情 / 健康 / 大运流年）
- [x] 🌐 Streamlit Web 界面，一键输入查看结果
- [x] 🗄️ 数据库记录 + 增删改查接口
- [x] 🔗 合盘功能（双人八字匹配/分析）快来看看他/她是不是你正确的另一半吧

## 📸 界面预览

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/6f8d5c62-5969-45f8-8846-ac1b270d2ea7" width="100%"></td>
    <td><img src="https://github.com/user-attachments/assets/90cca42e-4cbb-4948-b3d2-dd0cda2d7607" width="100%"></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><img src="https://github.com/user-attachments/assets/533e2ce8-8ce8-47f0-815f-53b22de8594b" width="80%"></td>
  </tr>
</table>

## 🚧 待优化

- [ ] 前端界面美化（考虑用 React 重构）
- [ ] 接入 RAG（检索古籍经典作为知识库）
- [ ] 其他...


<pre> ```cd backend

# 创建虚拟环境
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000``` </pre>



