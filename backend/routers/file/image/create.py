from fastapi import HTTPException, APIRouter, UploadFile, File
from data.data import Session, Image
import os
import uuid

router = APIRouter(
    prefix="/file/image",
)


@router.post("")
async def create(image: UploadFile = File(...)):
    """Загружает изображение на сервер и создаёт запись в БД."""
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    file_extension = os.path.splitext(image.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("data", "img", unique_filename)

    content = await image.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # Создаём запись в БД
    with Session() as session:
        new_image = Image(path=file_path)
        session.add(new_image)
        session.commit()
        session.refresh(new_image)

    return {
        "status": "success",
        "image_id": new_image.id,
        "image_name": unique_filename,
        "file_path": file_path,
        "size": len(content),
        "content_type": image.content_type
    }
