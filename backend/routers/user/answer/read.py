from fastapi import HTTPException, APIRouter, Query
from data.data import Session, Answer, Task, User, Image
from media import serialize_image

router = APIRouter(
    prefix="/user/answer",
)


@router.get("")
async def get_answers(
    master_token: str = Query(...),
    task_id: int = Query(None),
    answer_id: int = Query(None)
):
    """Возвращает ответы мастера."""
    with Session() as session:
        master = session.query(User).filter(User.token == master_token, User.is_master == True).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        if answer_id:
            # Получаем один ответ
            answer = session.query(Answer).filter(Answer.id == answer_id).first()
            if not answer:
                raise HTTPException(status_code=404, detail="Answer not found")

            task = session.query(Task).filter(Task.id == answer.task_id, Task.master_id == master.id).first()
            if not task:
                raise HTTPException(status_code=403, detail="Not enough permissions")

            answer_img = session.query(Image).filter(Image.id == answer.image_id).first() if answer.image_id else None
            image_data = serialize_image(answer_img)

            return {
                "status": "success",
                "answer": {
                    "id": answer.id,
                    "task_id": answer.task_id,
                    "content": answer.content,
                    "created_at": str(answer.created_at) if answer.created_at else None,
                    "image": image_data,
                    "comment": answer.comment,
                    "comment_grade": answer.comment_grade
                }
            }
        elif task_id:
            # Получаем все ответы задачи
            task = session.query(Task).filter(Task.id == task_id, Task.master_id == master.id).first()
            if not task:
                raise HTTPException(status_code=403, detail="Not enough permissions")

            answers = session.query(Answer).filter(Answer.task_id == task_id).all()
            result = []
            for answer in answers:
                answer_img = session.query(Image).filter(Image.id == answer.image_id).first() if answer.image_id else None
                image_data = serialize_image(answer_img)
                
                result.append({
                    "id": answer.id,
                    "task_id": answer.task_id,
                    "content": answer.content,
                    "created_at": str(answer.created_at) if answer.created_at else None,
                    "image": image_data,
                    "comment": answer.comment,
                    "comment_grade": answer.comment_grade
                })

            return {"status": "success", "task_id": task_id, "answers": result}
        else:
            # Получаем все ответы мастера
            tasks = session.query(Task).filter(Task.master_id == master.id).all()
            task_ids = [t.id for t in tasks]

            answers = session.query(Answer).filter(Answer.task_id.in_(task_ids)).all()
            result = []
            for answer in answers:
                answer_img = session.query(Image).filter(Image.id == answer.image_id).first() if answer.image_id else None
                image_data = serialize_image(answer_img)
                
                result.append({
                    "id": answer.id,
                    "task_id": answer.task_id,
                    "content": answer.content,
                    "created_at": str(answer.created_at) if answer.created_at else None,
                    "image": image_data,
                    "comment": answer.comment,
                    "comment_grade": answer.comment_grade
                })

            return {"status": "success", "answers": result}
