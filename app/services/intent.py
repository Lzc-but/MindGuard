"""用户意图分类服务 — 用 LLM 将用户输入分为 CHAT / CONSULT / RISK 三类"""

import logging

from app.models.llm import get_chat_model

logger = logging.getLogger(__name__)

INTENT_CLASSIFY_PROMPT = """你是一个用户意图分类器，只做意图识别，不回答问题。
用户输入内容：{user_input}

请将用户意图严格分为以下三类之一，只输出标签，不要其他任何内容：
- CHAT：日常闲聊、问候、天气、娱乐、无关内容
- CONSULT：心理咨询、情绪倾诉、压力、焦虑、低落、失眠、亲密关系、学习压力等心理相关
- RISK：自杀、自残、绝望、自伤、伤人、严重抑郁等高危内容"""


def classify_intent(user_input: str) -> str:
    """返回 CHAT / CONSULT / RISK；分类失败时默认 CONSULT（保守处理）"""
    try:
        model = get_chat_model()
        prompt = INTENT_CLASSIFY_PROMPT.format(user_input=user_input)
        response = model.invoke(prompt)
        result = str(response.content).strip().upper()
        if "RISK" in result:
            return "RISK"
        if "CONSULT" in result:
            return "CONSULT"
        return "CHAT"
    except Exception:
        logger.exception("Intent classification failed, falling back to CONSULT")
        return "CONSULT"