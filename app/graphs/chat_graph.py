"""

对话链路 LangGraph StateGraph —— 检索 + 生成 + 降级
"""
import logging
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate

from app.models.llm import get_chat_model
from app.services.retrieval import similarity_search

logger = logging.getLogger(__name__)

CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是一个心理健康助手，回答要安全、有同理心。"
               "如果用户有自残/自杀风险，必须建议立即联系紧急援助。"),
    ("system", "知识库上下文:\n{context}"),
    ("placeholder", "{history}"),
    ("human", "{question}"),
])


class ChatPipelineState(TypedDict):
    question: str
    history_messages: list
    context: str
    references: list[str]
    answer: str


def _retrieve_node(state: ChatPipelineState) -> dict:
    """从知识库检索相关上下文。即使检索失败也返回空结果，不中断链路。"""
    references = similarity_search(state["question"], k=3)
    context = "\n\n".join(references) if references else "No external context found."
    return {"context": context, "references": references}


def _generate_node(state: ChatPipelineState) -> dict:
    """构建 Prompt 并调用 LLM 生成回复。超时或失败时返回安全降级文案。"""
    try:
        model = get_chat_model()
        messages = CHAT_PROMPT.format_messages(
            context=state["context"],
            history=state["history_messages"],
            question=state["question"],
        )
        response = model.invoke(messages)
        return {"answer": str(response.content)}
    except Exception:
        logger.exception("LLM invoke failed in generate_node")
        return {
            "answer": (
                "非常抱歉，我暂时无法处理您的请求。请稍后再试。"
                "如果您正处于紧急情况，请立即联系学校心理中心或拨打心理援助热线。"
            ),
            "references": [],
        }


def build_chat_graph() -> StateGraph:
    graph = StateGraph(ChatPipelineState)

    graph.add_node("retrieve", _retrieve_node)
    graph.add_node("generate", _generate_node)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile()


# 模块级编译实例，全局复用
chat_graph = build_chat_graph()