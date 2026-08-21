import os
import uuid
from pathlib import Path
from app.config import get_settings

settings = get_settings()


def get_upload_dir() -> Path:
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def save_uploaded_file(filename: str, file_content: bytes) -> tuple[str, str]:
    ext = Path(filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    upload_dir = get_upload_dir()
    file_path = upload_dir / unique_name
    with open(file_path, "wb") as f:
        f.write(file_content)
    return unique_name, str(file_path)


def delete_file(file_path: str) -> bool:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except OSError:
        pass
    return False
