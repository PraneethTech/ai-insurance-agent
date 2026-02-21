"""
Documents router: upload, list, retrieve, download.
"""
import uuid, os, shutil, time
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

import config
from deps import get_current_user
from features.documents.schemas import UploadStartResponse
from features.documents.service import DocumentService
from features.documents.pipeline import DocumentPipeline

router = APIRouter(prefix="/documents", tags=["Documents"])
_svc = DocumentService()
_pipeline = DocumentPipeline()


@router.post("/", response_model=UploadStartResponse, status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    description: str | None = Form(None),
    user: dict = Depends(get_current_user),
):
    doc_id = str(uuid.uuid4())
    vector_id = f"vec_{uuid.uuid4().hex}"
    user_id = str(user["_id"])

    timestamp = int(time.time())
    safe_name = "".join(c for c in (file.filename or "upload") if c.isalnum() or c in "._-")
    stem, ext = os.path.splitext(safe_name)
    storage_name = f"{stem}_{user_id}_{timestamp}{ext}"
    file_path = str(config.UPLOADS_DIR / storage_name)

    with open(file_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    await _svc.create_record(doc_id=doc_id, user_id=user_id, filename=file.filename or safe_name,
                              vector_id=vector_id, file_path=file_path, description=description)

    background_tasks.add_task(_pipeline.run, doc_id=doc_id, user_id=user_id, file_path=file_path, vector_id=vector_id)

    return UploadStartResponse(doc_id=doc_id, upload_id=doc_id, vector_id=vector_id, vector_status="PROCESSING")


@router.get("/", tags=["Documents"])
async def list_documents(user: dict = Depends(get_current_user)):
    return await _svc.get_all(str(user["_id"]))


@router.get("/{doc_id}", tags=["Documents"])
async def get_document(doc_id: str, user: dict = Depends(get_current_user)):
    return await _svc.get_one(doc_id, str(user["_id"]))


@router.get("/{doc_id}/download", tags=["Documents"])
async def download_document(doc_id: str, user: dict = Depends(get_current_user)):
    doc = await _svc.get_one(doc_id, str(user["_id"]))
    file_path = doc.get("file_path", "")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    return FileResponse(file_path, filename=doc["filename"], media_type="application/pdf")
