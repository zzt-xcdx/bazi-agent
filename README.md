为了找一个ai agent实习，从零弄一个项目把
# 赛博算命 · 八字命理 Agent（WIP）

后端：Python + FastAPI + LangChain + DeepSeek  
前端：Streamlit

## 功能

- 根据出生信息排四柱八字（年、月、日、时）
- 调用 DeepSeek 进行命理分析（事业 / 感情 / 健康 / 大运流年）
- 简单 Web 界面（Streamlit）一键输入信息和查看结果

## 本地运行

### 后端

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
