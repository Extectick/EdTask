from fastapi import HTTPException, APIRouter, UploadFile, File as FastAPIFile
from data.data import Session, File as DBFile
import os
import uuid

router = APIRouter(
    prefix="/file/file",
)


@router.post("")
async def create(file: UploadFile = FastAPIFile(...)):
    """Загружает файл на сервер и создаёт запись в БД."""
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("data", "files", unique_filename)

    os.makedirs("data/files", exist_ok=True)

    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # Создаём запись в БД
    with Session() as session:
        new_file = DBFile(path=file_path, original_name=file.filename)
        session.add(new_file)
        session.commit()
        session.refresh(new_file)

    return {
        "status": "success",
        "file_id": new_file.id,
        "file_name": unique_filename,
        "original_name": file.filename,
        "file_path": file_path,
        "size": len(content),
        "content_type": file.content_type
    }


@router.get("/{file_name}")
async def download(file_name: str):
    """Скачивает файл по имени."""
    file_path = os.path.join("data", "files", file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    from fastapi.responses import FileResponse
    return FileResponse(file_path, filename=file_name)
