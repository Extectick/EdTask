from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from data.data import Session, Answer, Task, User

router = APIRouter(
    prefix="/user/answer",
)


class DeleteAnswerSchema(BaseModel):
    answer_id: int
    master_token: str


@router.delete("")
async def delete(data: DeleteAnswerSchema):
    """Удаляет ответ."""
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

        # Удаляем ответ
        session.delete(answer)
        session.commit()

        return {"status": "success", "answer_id": data.answer_id}
