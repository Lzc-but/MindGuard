# 心护AI智能体（mental_guard_ai）

基于 `LangChain + FastAPI + FAISS + JWT/OAuth2` 的聊天与心理监控一体化服务。

## 功能概览

- 对接 Ollama/OpenAI，提供多轮心理问答
- 管理员上传知识库并重建 FAISS 向量索引
- 基于规则化心理状态识别（可替换为 LoRA 微调模型推理）
- 通过 MCP 接口回传心理状态数据
- 自动将心理记录导出为 Excel
- 基于 JWT + OAuth2 的管理员/普通用户权限隔离

## 项目结构

已按如下目录实现：

- `app/`：FastAPI 主体、API、服务层、模型与工具
- `data/`：知识库、向量索引、Excel 导出、日志
- `models/finetuned/`：微调模型目录占位

## 快速启动

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置环境变量

```bash
cp .env.example .env
```

3. 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4. 打开文档

- Swagger: `http://127.0.0.1:8000/docs`
- 健康检查: `http://127.0.0.1:8000/health`

## 默认账户

- 管理员：`admin / admin123`
- 普通用户：`user / user123`

> 生产环境请务必在 `.env` 中修改默认账号和 `JWT_SECRET_KEY`。

## 核心接口

- `POST /api/auth/login`：登录获取 JWT
- `GET /api/auth/me`：当前用户信息
- `POST /api/knowledge/upload`：管理员上传知识库（`.txt/.md`）
- `POST /api/knowledge/rebuild`：管理员重建向量索引
- `POST /api/chat`：基于 RAG 的问答接口
- `POST /api/mental/analyze`：心理状态识别 + MCP 推送 + Excel 导出

## LoRA 微调模型接入说明

当前 `app/services/mental.py` 为可运行 MVP（规则版），你可替换为真实模型推理逻辑：

1. 将 LoRA/PEFT 权重放到 `models/finetuned/`
2. 在 `app/models/llm.py` 或 `app/services/mental.py` 中加载微调模型
3. 返回统一结构：
   - `status`: `high_risk | medium_risk | low_risk`
   - `score`: `0-1` 概率
   - `suggestion`: 干预建议
