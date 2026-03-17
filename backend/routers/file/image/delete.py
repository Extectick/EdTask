from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

from data.data import Image, Session
from media import delete_image

router = APIRouter(
    prefix="/file/image",
)


class DeleteImageSchema(BaseModel):
    image_id: int | None = None
    image_name: str | None = None
    image_url: str | None = None


@router.delete("")
async def delete(data: DeleteImageSchema):
    """Удаляет изображение из MinIO и БД."""
    with Session() as session:
        image = None
        if data.image_id is not None:
            image = session.query(Image).filter(Image.id == data.image_id).first()
        elif data.image_url:
            image = session.query(Image).filter(Image.path == data.image_url).first()
        elif data.image_name:
            image = session.query(Image).filter(Image.path.like(f"%/{data.image_name}")).first()

        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        delete_image(image.path)
        image_name = image.path.rstrip("/").split("/")[-1]
        image_url = image.path
        session.delete(image)
        session.commit()

        return {
            "status": "success",
            "image_id": image.id,
            "image_name": image_name,
            "image_url": image_url,
        }
