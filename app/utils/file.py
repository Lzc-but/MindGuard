from pathlib import Path

from app.core.config import settings


def ensure_data_dirs() -> None:
    for path in [
        settings.knowledge_path,
        settings.vector_store_path,
        settings.exports_path,
        settings.logs_path,
    ]:
        Path(path).mkdir(parents=True, exist_ok=True)
