import sqlite3
import uuid
from datetime import datetime, timezone

from app.core.config import settings
from app.models.llm import get_chat_model
from app.services.rag import similarity_search
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_chat_db() -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_deleted INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def create_conversation(user_id: str, title: str | None = None) -> dict:
    now = _utc_now()
    conversation_id = str(uuid.uuid4())
    name = (title or "").strip() or "新对话"
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO conversations (id, user_id, title, created_at, updated_at, is_deleted)
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (conversation_id, user_id, name, now, now),
        )
        conn.commit()
        return {
            "id": conversation_id,
            "title": name,
            "created_at": now,
            "updated_at": now,
        }
    finally:
        conn.close()


def get_or_create_conversation(user_id: str, conversation_id: str) -> dict:
    conn = _connect()
    try:
        row = conn.execute(
            """
            SELECT id, title, created_at, updated_at
            FROM conversations
            WHERE id = ? AND user_id = ? AND is_deleted = 0
            """,
            (conversation_id, user_id),
        ).fetchone()
        if row:
            return dict(row)
    finally:
        conn.close()

    now = _utc_now()
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO conversations (id, user_id, title, created_at, updated_at, is_deleted)
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (conversation_id, user_id, "新对话", now, now),
        )
        conn.commit()
        return {
            "id": conversation_id,
            "title": "新对话",
            "created_at": now,
            "updated_at": now,
        }
    finally:
        conn.close()


def list_conversations(user_id: str) -> list[dict]:
    conn = _connect()
    try:
        rows = conn.execute(
            """
            SELECT id, title, created_at, updated_at
            FROM conversations
            WHERE user_id = ? AND is_deleted = 0
            ORDER BY updated_at DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def delete_conversation(user_id: str, conversation_id: str) -> None:
    conn = _connect()
    try:
        row = conn.execute(
            """
            SELECT id FROM conversations
            WHERE id = ? AND user_id = ? AND is_deleted = 0
            """,
            (conversation_id, user_id),
        ).fetchone()
        if not row:
            raise ValueError("Conversation not found")
        now = _utc_now()
        conn.execute(
            """
            UPDATE conversations
            SET is_deleted = 1, updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (now, conversation_id, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def rename_conversation(user_id: str, conversation_id: str, title: str) -> dict:
    new_title = title.strip()
    if not new_title:
        raise ValueError("Conversation title cannot be empty")
    if len(new_title) > 50:
        raise ValueError("Conversation title must be <= 50 characters")

    conn = _connect()
    try:
        row = conn.execute(
            """
            SELECT id, created_at FROM conversations
            WHERE id = ? AND user_id = ? AND is_deleted = 0
            """,
            (conversation_id, user_id),
        ).fetchone()
        if not row:
            raise ValueError("Conversation not found")

        now = _utc_now()
        conn.execute(
            """
            UPDATE conversations
            SET title = ?, updated_at = ?
            WHERE id = ? AND user_id = ? AND is_deleted = 0
            """,
            (new_title, now, conversation_id, user_id),
        )
        conn.commit()
        return {
            "id": conversation_id,
            "title": new_title,
            "created_at": row["created_at"],
            "updated_at": now,
        }
    finally:
        conn.close()


def get_conversation_messages(user_id: str, conversation_id: str) -> list[dict]:
    conn = _connect()
    try:
        row = conn.execute(
            """
            SELECT id FROM conversations
            WHERE id = ? AND user_id = ? AND is_deleted = 0
            """,
            (conversation_id, user_id),
        ).fetchone()
        if not row:
            raise ValueError("Conversation not found")
        rows = conn.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            """,
            (conversation_id,),
        ).fetchall()
        return [dict(item) for item in rows]
    finally:
        conn.close()


def _insert_message(conn: sqlite3.Connection, conversation_id: str, role: str, content: str) -> None:
    conn.execute(
        """
        INSERT INTO messages (id, conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (str(uuid.uuid4()), conversation_id, role, content, _utc_now()),
    )


def _ensure_conversation_exists(conn: sqlite3.Connection, user_id: str, conversation_id: str) -> None:
    row = conn.execute(
        """
        SELECT id FROM conversations
        WHERE id = ? AND user_id = ? AND is_deleted = 0
        """,
        (conversation_id, user_id),
    ).fetchone()
    if not row:
        raise ValueError("Conversation not found")


def _build_history_messages(conn: sqlite3.Connection, conversation_id: str) -> list:
    rows = conn.execute(
        """
        SELECT role, content
        FROM (
            SELECT role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at DESC
            LIMIT 8
        ) t
        ORDER BY created_at ASC
        """,
        (conversation_id,),
    ).fetchall()

    messages = []
    for row in rows:
        if row["role"] == "assistant":
            messages.append(AIMessage(content=row["content"]))
        elif row["role"] == "user":
            messages.append(HumanMessage(content=row["content"]))
    return messages


def _maybe_update_title(conn: sqlite3.Connection, conversation_id: str, question: str) -> None:
    row = conn.execute(
        """
        SELECT title FROM conversations
        WHERE id = ?
        """,
        (conversation_id,),
    ).fetchone()
    if not row:
        return
    current_title = row["title"]
    if current_title != "新对话":
        return
    new_title = question.strip().replace("\n", " ")[:20] or "新对话"
    conn.execute(
        """
        UPDATE conversations
        SET title = ?, updated_at = ?
        WHERE id = ?
        """,
        (new_title, _utc_now(), conversation_id),
    )


def chat_in_conversation(user_id: str, conversation_id: str, question: str) -> tuple[str, list[str]]:
    conn = _connect()
    try:
        _ensure_conversation_exists(conn, user_id, conversation_id)

        references = similarity_search(question, k=3)
        context = "\n\n".join(references) if references else "No external context found."

        model = get_chat_model()
        system_prompt = (
            "你是一个心理健康助手，回答要安全、有同理心。"
            "如果用户有自残/自杀风险，必须建议立即联系紧急援助。"
        )
        history_messages = _build_history_messages(conn, conversation_id)
        messages = [
            SystemMessage(content=system_prompt),
            SystemMessage(content=f"Knowledge base context:\n{context}"),
            *history_messages,
            HumanMessage(content=question),
        ]

        response = model.invoke(messages)
        answer = str(response.content)

        _insert_message(conn, conversation_id, "user", question)
        _insert_message(conn, conversation_id, "assistant", answer)
        conn.execute(
            """
            UPDATE conversations
            SET updated_at = ?
            WHERE id = ?
            """,
            (_utc_now(), conversation_id),
        )
        _maybe_update_title(conn, conversation_id, question)
        conn.commit()
        return answer, references
    finally:
        conn.close()
