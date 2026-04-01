from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.mental import MentalRequest, MentalResponse
from app.services.excel import export_mental_record
from app.services.mcp import push_mental_state
from app.services.mental import detect_mental_state

router = APIRouter(prefix="/api/mental", tags=["mental"])


@router.post("/analyze", response_model=MentalResponse)
async def analyze_mental_state(
    payload: MentalRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> MentalResponse:
    result = detect_mental_state(payload.text)
    record = {
        "user_id": payload.user_id,
        "operator": current_user["username"],
        "status": result.status,
        "score": result.score,
        "suggestion": result.suggestion,
        "text": payload.text,
    }
    export_path = export_mental_record(record)
    await push_mental_state({**record, "excel_file": export_path})
    return result
