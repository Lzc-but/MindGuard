from datetime import datetime
from pathlib import Path

import pandas as pd

from app.core.config import settings


def export_mental_record(record: dict) -> str:
    out_dir = Path(settings.exports_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = out_dir / f"mental_records_{datetime.now().strftime('%Y%m%d')}.xlsx"

    row = pd.DataFrame([record])
    if filename.exists():
        existing = pd.read_excel(filename)
        row = pd.concat([existing, row], ignore_index=True)
    row.to_excel(filename, index=False)
    return str(filename)
