为了找一个ai agent实习，做一个ai项目,反向学习一波
# 生成四柱八字排盘 | 进行命理分析

后端：Python + FastAPI + LangChain + DeepSeek  
前端：Streamlit

## 功能

- 根据出生信息排四柱八字（年、月、日、时）
- 调用 DeepSeek 进行命理分析（事业 / 感情 / 健康 / 大运流年）
- 简单 Web 界面（Streamlit）一键输入信息和查看结果


###更新
数据库记录+增删改接口，合盘功能
<img width="1840" height="1051" alt="image" src="https://github.com/user-attachments/assets/6f8d5c62-5969-45f8-8846-ac1b270d2ea7" />
<img width="1866" height="1077" alt="image" src="https://github.com/user-attachments/assets/90cca42e-4cbb-4948-b3d2-dd0cda2d7607" />
<img width="1954" height="1189" alt="image" src="https://github.com/user-attachments/assets/533e2ce8-8ce8-47f0-815f-53b22de8594b" />

###待优化
之后优化前端界面，考虑增加RAG(感觉这个场景不太好用)
## 本地运行
### 后端

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
      ```


