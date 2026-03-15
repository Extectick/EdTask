from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional
from data.data import Session, Answer, Task, User, Image

router = APIRouter(
    prefix="/user/answer",
)


class UpdateAnswerSchema(BaseModel):
    answer_id: int
    content: Optional[str] = None
    image_id: Optional[int] = None
    comment: Optional[str] = None
    comment_grade: Optional[int] = None
    master_token: str


@router.patch("")
async def update(data: UpdateAnswerSchema):
    """Обновляет ответ (мастер может добавить comment и comment_grade)."""
    with Session() as session:
        master = session.query(User).filter(User.token == data.master_token, User.is_master == True).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        answer = session.query(Answer).filter(Answer.id == data.answer_id).first()
        if not answer:
            raise HTTPException(status_code=404, detail="Answer not found")

        task = session.query(Task).filter(Task.id == answer.task_id, Task.master_id == master.id).first()
        if not task:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Обновляем поля
        if data.content is not None:
            answer.content = data.content
        if data.image_id is not None:
            answer.image_id = data.image_id
        if data.comment is not None:
            answer.comment = data.comment
        if data.comment_grade is not None:
            answer.comment_grade = data.comment_grade

        session.commit()
        session.refresh(answer)

        return {
            "status": "success",
            "answer_id": answer.id,
            "content": answer.content,
            "comment": answer.comment,
            "comment_grade": answer.comment_grade
        }
