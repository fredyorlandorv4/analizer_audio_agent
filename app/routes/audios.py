
import uuid
from pathlib import Path
from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Request,Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db, SessionLocal
from ..models import Audio
from ..schemas import AudioOut
from ..security import get_current_user
from ..utils import ensure_user_dir
import base64
from ..security import get_current_user


router = APIRouter(prefix="/audios", tags=["audios"])



def audio_to_base64(file_path: str) -> str:
    """
    Convierte un archivo de audio a una cadena base64 (UTF-8).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    with path.open("rb") as audio_file:
        audio_bytes = audio_file.read()
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return audio_b64
    


async def _notify_webhook(audio: Audio, download_url: str):
    if not settings.WEBHOOK_URL:
        return None, None
    payload = {
        "audio_id": audio.id,
        "user_id": audio.user_id,
        "original_filename": audio.original_filename,
        "content_type": audio.content_type,
        "size_bytes": audio.size_bytes,
        "created_at": audio.created_at.isoformat(),
        "download_url": download_url,
        "base64":audio_to_base64(audio.stored_path)
    }
    async with httpx.AsyncClient(timeout=settings.WEBHOOK_TIMEOUT_SECONDS) as client:
        try:
            resp = await client.post(settings.WEBHOOK_URL, json=payload)
            return resp.status_code, resp.text
        except Exception as e:
            return None, str(e)

@router.post("", response_model=AudioOut, status_code=201)
async def upload_audio(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Archivo inválido")

    user_dir = ensure_user_dir(current_user.id)
    ext = Path(file.filename).suffix or ""
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = user_dir / stored_name

    size_bytes = 0
    with stored_path.open("wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size_bytes += len(chunk)
            out.write(chunk)

    audio = Audio(
        user_id=current_user.id,
        original_filename=file.filename,
        stored_filename=stored_name,
        stored_path=str(stored_path.resolve()),
        content_type=file.content_type,
        size_bytes=size_bytes,
        webhook_url=settings.WEBHOOK_URL,
        webhook_status="pending" if settings.WEBHOOK_URL else None,
    )
    db.add(audio)
    db.commit()
    db.refresh(audio)

    # Base URL para enlaces absolutos
    base_url = settings.PUBLIC_BASE_URL
    if not base_url:
        host = request.headers.get("x-forwarded-host") or request.headers.get("host")
        proto = request.headers.get("x-forwarded-proto") or request.url.scheme
        base_url = f"{proto}://{host}" if host else str(request.base_url).rstrip("/")

    download_url = f"{base_url}/audios/{audio.id}/file"

    async def _notify_and_persist(audio_id: int):
        status_code, body = await _notify_webhook(audio, download_url)
        with SessionLocal() as s:
            a = s.query(Audio).get(audio_id)
            if a:
                if status_code is None:
                    a.webhook_status = "failed"
                else:
                    a.webhook_status = "sent" if 200 <= status_code < 300 else "failed"
                a.webhook_response_code = status_code
                a.webhook_response_body = (body or "")[:4000]
                s.commit()

    if settings.WEBHOOK_URL:
        background_tasks.add_task(_notify_and_persist, audio.id)

    return AudioOut(
        id=audio.id,
        original_filename=audio.original_filename,
        content_type=audio.content_type,
        size_bytes=audio.size_bytes,
        created_at=audio.created_at,
        download_url=f"/audios/{audio.id}/file",
    )

@router.get("", response_model=List[AudioOut])
def list_audios(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    items = (
        db.query(Audio)
        .filter(Audio.user_id == current_user.id)
        .order_by(Audio.created_at.desc())
        .all()
    )
    return [
        AudioOut(
            id=i.id,
            original_filename=i.original_filename,
            content_type=i.content_type,
            size_bytes=i.size_bytes,
            created_at=i.created_at,
            download_url=f"/audios/{i.id}/file",
        )
        for i in items
    ]

@router.get("/{audio_id}", response_model=AudioOut)
def get_audio(audio_id: int,current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Audio).get(audio_id)
    if not a or a.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Audio no encontrado")
    return AudioOut(
        id=a.id,
        original_filename=a.original_filename,
        content_type=a.content_type,
        size_bytes=a.size_bytes,
        created_at=a.created_at,
        download_url=f"/audios/{a.id}/file",
    )

@router.get("/{audio_id}/file")
def download_audio(audio_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Audio).get(audio_id)
    if not a or a.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Audio no encontrado")
    path = Path(a.stored_path)
    if not path.exists():
        raise HTTPException(status_code=410, detail="Archivo no disponible")
    filename = a.original_filename or path.name
    return FileResponse(path, media_type=a.content_type or "application/octet-stream", filename=filename)


@router.post("/audios/{audio_id}/extra")
def webhook_update_extra(
    audio_id: int,
    body: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    mode: str = Query("merge", regex="^(merge|replace)$"),
):


    if "extra" not in body or not isinstance(body["extra"], dict):
        raise HTTPException(status_code=400, detail="Se requiere 'extra' como objeto JSON")

    a = db.query(Audio).get(audio_id)
    if not a:
        raise HTTPException(status_code=404, detail="Audio no encontrado")

    if mode == "replace":
        a.extra = body["extra"]
    else:
        existing = a.extra or {}
        merged = dict(existing)
        merged.update(body["extra"])
        a.extra = merged

    db.add(a)
    db.commit()
    db.refresh(a)

    return {"ok": True, "audio_id": a.id, "extra": a.extra}