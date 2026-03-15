from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
import os

router = APIRouter(
    prefix="/file/image",
)


class DeleteImageSchema(BaseModel):
    image_name: str


@router.delete("")
async def delete(data: DeleteImageSchema):
    """Удаляет изображение с сервера."""
    file_path = os.path.join("data", "img", data.image_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    os.remove(file_path)
    
    return {"status": "success", "image_name": data.image_name}
