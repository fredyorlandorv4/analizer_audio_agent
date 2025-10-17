
from pathlib import Path
from .config import settings

def ensure_user_dir(user_id: int) -> Path:
    media_root = Path(settings.MEDIA_ROOT)
    media_root.mkdir(parents=True, exist_ok=True)
    user_dir = media_root / f"user_{user_id}"
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir
