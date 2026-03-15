from fastapi import HTTPException, APIRouter, Query
from data.data import Session, Task, TaskImage, Image, User, Answer

router = APIRouter(
    prefix="/student/task",
)


@router.get("")
async def get_tasks(
    user_token: str = Query(...),
    task_id: int = Query(None)
):
    """Возвращает задачи назначенные ученику."""
    with Session() as session:
        # Проверяем что пользователь существует и это ученик
        student = session.query(User).filter(User.token == user_token, User.is_master == False).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        if task_id:
            # Получаем одну задачу
            task = session.query(Task).filter(
                Task.id == task_id,
                Task.user_id == student.token,
                Task.is_active == True
            ).first()
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            task_images = session.query(TaskImage).filter(TaskImage.task_id == task.id).all()
            images = []
            for ti in task_images:
                img = session.query(Image).filter(Image.id == ti.image_id).first()
                if img and img.path:
                    image_name = img.path.split('/')[-1].split('\\')[-1]
                    images.append({"id": img.id, "image_name": image_name})

            # Ответы этого ученика
            student_answers = session.query(Answer).filter(
                Answer.task_id == task.id
            ).all()
            answers_data = []
            for answer in student_answers:
                answer_img = None
                if answer.image_id:
                    answer_img = session.query(Image).filter(Image.id == answer.image_id).first()
                
                image_data = None
                if answer_img and answer_img.path:
                    image_name = answer_img.path.split('/')[-1].split('\\')[-1]
                    image_data = {"id": answer_img.id, "image_name": image_name}
                
                answers_data.append({
                    "id": answer.id,
                    "content": answer.content,
                    "created_at": str(answer.created_at) if answer.created_at else None,
                    "image": image_data,
                    "comment": answer.comment,
                    "comment_grade": answer.comment_grade
                })

            return {
                "status": "success",
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.content,
                    "is_active": task.is_active,
                    "created_at": str(task.created_at) if task.created_at else None,
                    "images": images,
                    "my_answers": answers_data
                }
            }
        else:
            # Получаем все задачи назначенные этому ученику
            tasks = session.query(Task).filter(
                Task.user_id == student.token,
                Task.is_active == True
            ).all()

            result = []
            for task in tasks:
                task_images = session.query(TaskImage).filter(TaskImage.task_id == task.id).all()
                images = [{"id": img.id, "path": img.path} for ti in task_images 
                          if (img := session.query(Image).filter(Image.id == ti.image_id).first())]

                # Ответы этого ученика
                student_answers = session.query(Answer).filter(
                    Answer.task_id == task.id
                ).all()
                answers_data = [{
                    "id": answer.id,
                    "content": answer.content,
                    "created_at": str(answer.created_at) if answer.created_at else None,
                    "image": {"id": session.query(Image).filter(Image.id == answer.image_id).first().id, 
                              "path": session.query(Image).filter(Image.id == answer.image_id).first().path} 
                              if answer.image_id else None,
                    "comment": answer.comment,
                    "comment_grade": answer.comment_grade
                } for answer in student_answers]

                result.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.content,
                    "is_active": task.is_active,
                    "created_at": str(task.created_at) if task.created_at else None,
                    "images": images,
                    "my_answers": answers_data
                })

            return {"status": "success", "user_id": student.token, "tasks": result, "count": len(result)}
