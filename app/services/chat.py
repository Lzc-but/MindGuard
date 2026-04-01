from collections import defaultdict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.models.llm import get_chat_model
from app.services.rag import similarity_search

# ====================== 全局变量：会话记忆 ======================
# 结构：{ "会话ID": [对话历史列表] }
# 作用：让 AI 记住之前聊了什么，实现多轮对话
SESSION_MESSAGES: dict[str, list] = defaultdict(list)


def chat_with_context(
        session_id: str,  # 会话ID（区分不同用户/不同聊天窗口）
        question: str     # 用户当前的问题
        ) -> tuple[str, list[str]]:  # 返回：AI回答 + 引用片段
    
    # 1. 从【知识库】中检索和用户问题相关的内容（取最相关的3条）
    references = similarity_search(question, k=3)

    # 2. 把检索到的知识库内容拼接成一段文字
    context = "\n\n".join(references) if references else "No external context found."

    # 3. 加载大模型
    model = get_chat_model()

    # 4. 给 AI 设定系统角色：心理助手 + 安全规则
    system_prompt = (
        "你是一个心理健康助手，回答要安全、有同理心。"
        "如果用户有自残/自杀风险，必须建议立即联系紧急援助。"
    )

    # 5. 组装给大模型的所有消息
    messages = [
        SystemMessage(content=system_prompt),
        SystemMessage(content=f"Knowledge base context:\n{context}"),
        *SESSION_MESSAGES[session_id][-8:], # 把当前用户最近 8 轮聊天历史，放进 AI 上下文里
        HumanMessage(content=question),
    ]

    # 6. 把所有消息发给大模型，获取回答
    response = model.invoke(messages)

    # 7. 把【用户问题】和【AI回答】存入会话记忆，下次对话能记住
    SESSION_MESSAGES[session_id].append(HumanMessage(content=question))
    SESSION_MESSAGES[session_id].append(AIMessage(content=response.content))

    # 8. 返回 AI 回答 + 引用的知识库片段
    return str(response.content), references
