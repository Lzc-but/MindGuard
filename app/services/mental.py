from app.schemas.mental import MentalResponse


RISK_KEYWORDS = {
    "high": ["自杀", "不想活", "结束生命", "伤害自己"],
    "medium": ["焦虑", "失眠", "崩溃", "抑郁", "压力很大"],
}


def detect_mental_state(text: str) -> MentalResponse:
    content = text.strip().lower()
    for keyword in RISK_KEYWORDS["high"]:
        if keyword in content:
            return MentalResponse(
                status="high_risk",
                score=0.9,
                suggestion="检测到高风险情绪，请立即联系学校心理中心或紧急热线。",
            )
    for keyword in RISK_KEYWORDS["medium"]:
        if keyword in content:
            return MentalResponse(
                status="medium_risk",
                score=0.7,
                suggestion="建议尽快预约心理咨询，并持续记录近期情绪变化。",
            )
    return MentalResponse(
        status="low_risk",
        score=0.2,
        suggestion="当前状态总体稳定，可通过运动和规律作息继续保持。",
    )
