import httpx

from app.core.config import settings


async def push_mental_state(payload: dict) -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(settings.mcp_endpoint, json=payload)
            return response.status_code < 300
    except Exception:
        return False
