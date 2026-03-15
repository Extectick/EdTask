from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional, List
from data.data import Session, Answer, Task, User, Image

router = APIRouter(
    prefix="/user/answer",
)


class CreateAnswerSchema(BaseModel):
    task_id: int
    content: str
    image_id: Optional[int] = None  # ID изображения для привязки


@router.post("")
async def create(data: CreateAnswerSchema):
    """Создаёт новый ответ."""
    with Session() as session:
        # Получаем задачу чтобы проверить что она существует
        task = session.query(Task).filter(Task.id == data.task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Проверяем что задача активна
        if not task.is_active:
            raise HTTPException(status_code=403, detail="Task is not active")

        new_answer = Answer(
            task_id=data.task_id,
            user_id=task.user_id,  # Сохраняем токен ученика которому назначена задача
            content=data.content,
            image_id=data.image_id
        )
        session.add(new_answer)
        session.commit()
        session.refresh(new_answer)

        return {
            "status": "success",
            "answer_id": new_answer.id,
            "task_id": new_answer.task_id,
            "content": new_answer.content
        }
