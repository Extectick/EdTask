from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
import os

router = APIRouter(
    prefix="/file/file",
)


class DeleteFileSchema(BaseModel):
    file_name: str


@router.delete("")
async def delete(data: DeleteFileSchema):
    """Удаляет файл с сервера."""
    file_path = os.path.join("data", "files", data.file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(file_path)

    return {"status": "success", "file_name": data.file_name}
