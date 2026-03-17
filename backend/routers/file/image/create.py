from fastapi import HTTPException, APIRouter, UploadFile, File
from data.data import Session, Image
from media import upload_image

router = APIRouter(
    prefix="/file/image",
)


@router.post("")
async def create(image: UploadFile = File(...)):
    """Загружает изображение на сервер и создаёт запись в БД."""
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    content = await image.read()
    object_name, image_url = upload_image(content, image.filename, image.content_type)

    # Создаём запись в БД
    with Session() as session:
        new_image = Image(path=image_url)
        session.add(new_image)
        session.commit()
        session.refresh(new_image)

    return {
        "status": "success",
        "image_id": new_image.id,
        "image_name": object_name.split("/")[-1],
        "image_url": image_url,
        "file_path": image_url,
        "size": len(content),
        "content_type": image.content_type
    }
