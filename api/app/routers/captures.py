import json
import uuid
import asyncio
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Request
from fastapi.responses import HTMLResponse, Response, RedirectResponse, JSONResponse
import httpx

from app.config import CAPTURES_DIR, OCR_URL
from app.templates import templates

router = APIRouter()


def list_captures(offset=0, limit=20):
    capture_dir = Path(CAPTURES_DIR)
    if not capture_dir.exists():
        return [], 0

    entries = []
    try:
        for entry in capture_dir.iterdir():
            if entry.is_dir():
                image = entry / "image.png"
                if image.exists():
                    mtime = image.stat().st_mtime
                    entries.append((entry.name, mtime))
    except OSError:
        return [], 0

    entries.sort(key=lambda x: x[1], reverse=True)
    total = len(entries)
    page = entries[offset:offset + limit]
    return page, total


async def run_ocr(capture_id: str):
    capture_dir = Path(CAPTURES_DIR) / capture_id
    image_path = capture_dir / "image.png"

    if not image_path.exists():
        return

    image_bytes = image_path.read_bytes()

    for attempt in range(5):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{OCR_URL}/ocr",
                    files={"image": ("image.png", image_bytes, "image/png")},
                )
                resp.raise_for_status()
                ocr_data = resp.json()
                break
        except Exception as e:
            if attempt < 4:
                await asyncio.sleep(2 ** attempt)
            else:
                ocr_data = {"error": str(e), "words": []}

    ocr_path = capture_dir / "ocr.json"
    ocr_path.write_text(json.dumps(ocr_data, ensure_ascii=False))


@router.get("/")
async def index(request: Request):
    page, total = list_captures(0, 20)
    captures = [{"id": id, "timestamp": int(mtime)} for id, mtime in page]
    return templates.TemplateResponse(request, "index.html", {
        "captures": captures,
        "has_more": total > 20,
    })


@router.get("/gallery")
async def gallery(request: Request, offset: int = 0, limit: int = 20):
    page, total = list_captures(offset, limit)
    captures = [{"id": id, "timestamp": int(mtime)} for id, mtime in page]
    has_more = (offset + limit) < total
    return templates.TemplateResponse(request, "gallery.html", {
        "captures": captures,
        "has_more": has_more,
        "next_offset": offset + limit,
        "limit": limit,
    })


@router.post("/captures")
async def create_capture(
    image: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    request: Request = None,
):
    capture_id = str(uuid.uuid4())
    capture_dir = Path(CAPTURES_DIR) / capture_id
    capture_dir.mkdir(parents=True, exist_ok=True)

    contents = await image.read()
    image_path = capture_dir / "image.png"
    image_path.write_bytes(contents)

    if background_tasks:
        background_tasks.add_task(run_ocr, capture_id)
    else:
        asyncio.create_task(run_ocr(capture_id))

    is_htmx = request and request.headers.get("HX-Request") == "true"
    if is_htmx:
        resp = Response()
        resp.headers["HX-Redirect"] = f"/viewer/{capture_id}"
        return resp
    else:
        return RedirectResponse(url=f"/viewer/{capture_id}", status_code=303)


@router.delete("/captures/{capture_id}")
async def delete_capture(capture_id: str, request: Request, redirect: bool = False):
    capture_dir = Path(CAPTURES_DIR) / capture_id
    if not capture_dir.exists():
        raise HTTPException(status_code=404, detail="Capture not found")
    shutil.rmtree(str(capture_dir))

    is_htmx = request.headers.get("HX-Request") == "true"
    if is_htmx and redirect:
        resp = Response()
        resp.headers["HX-Redirect"] = "/"
        return resp
    elif is_htmx:
        return Response()
    else:
        return RedirectResponse(url="/", status_code=303)


@router.post("/captures/{capture_id}/ocr")
async def redo_ocr(capture_id: str, background_tasks: BackgroundTasks):
    capture_dir = Path(CAPTURES_DIR) / capture_id
    image_path = capture_dir / "image.png"
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Capture not found")
    ocr_path = capture_dir / "ocr.json"
    if ocr_path.exists():
        ocr_path.unlink()
    background_tasks.add_task(run_ocr, capture_id)
    return Response(status_code=204, headers={"HX-Trigger": "redo-ocr"})


@router.put("/captures/{capture_id}/ocr")
async def update_ocr(capture_id: str, data: dict = None):
    if data is None:
        data = {}
    capture_dir = Path(CAPTURES_DIR) / capture_id
    ocr_path = capture_dir / "ocr.json"
    if not ocr_path.exists():
        raise HTTPException(status_code=404, detail="OCR not ready yet")
    words = data.get("words", [])
    ocr_path.write_text(json.dumps({"words": words}, ensure_ascii=False))
    return {"status": "ok"}


@router.get("/captures/{capture_id}/ocr")
async def get_ocr(capture_id: str):
    ocr_path = Path(CAPTURES_DIR) / capture_id / "ocr.json"
    if not ocr_path.exists():
        raise HTTPException(status_code=404, detail="OCR not ready yet")
    content = ocr_path.read_text()
    return JSONResponse(content=json.loads(content))


@router.get("/viewer/{capture_id}", response_class=HTMLResponse)
async def viewer(request: Request, capture_id: str):
    capture_dir = Path(CAPTURES_DIR) / capture_id
    image_path = capture_dir / "image.png"
    ocr_path = capture_dir / "ocr.json"

    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Capture not found")

    ocr_ready = ocr_path.exists()

    return templates.TemplateResponse(request, "viewer.html", {
        "capture_id": capture_id,
        "ocr_ready": ocr_ready,
    })
