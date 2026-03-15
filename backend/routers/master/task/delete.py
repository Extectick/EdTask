from fastapi import HTTPException, APIRouter, Form
from data.data import Session, Task, TaskImage, TaskFile, Image, File, User, Answer

router = APIRouter(
    prefix="/master/task",
)


@router.post("/delete")
async def delete(
    task_id: int = Form(...),
    master_token: str = Form(...)
):
    """Удаляет задачу и все связанные данные."""
    with Session() as session:
        # Проверяем что мастер существует
        master = session.query(User).filter(User.token == master_token, User.is_master == True).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Проверяем что задача существует и принадлежит мастеру
        task = session.query(Task).filter(
            Task.id == task_id,
            Task.master_id == master.id
        ).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Удаляем изображения задачи
        task_images = session.query(TaskImage).filter(TaskImage.task_id == task_id).all()
        for ti in task_images:
            # Удаляем файл с диска
            import os
            img = session.query(Image).filter(Image.id == ti.image_id).first()
            if img and img.path:
                if os.path.exists(img.path):
                    os.remove(img.path)
                session.delete(img)
        
        # Удаляем файлы задачи
        task_files = session.query(TaskFile).filter(TaskFile.task_id == task_id).all()
        for tf in task_files:
            # Удаляем файл с диска
            import os
            file = session.query(File).filter(File.id == tf.file_id).first()
            if file and file.path:
                if os.path.exists(file.path):
                    os.remove(file.path)
                session.delete(file)
        
        # Удаляем ответы и их изображения
        answers = session.query(Answer).filter(Answer.task_id == task_id).all()
        for answer in answers:
            answer_images = session.query(TaskImage).filter(TaskImage.answer_id == answer.id).all()
            for ai in answer_images:
                img = session.query(Image).filter(Image.id == ai.image_id).first()
                if img and img.path:
                    if os.path.exists(img.path):
                        os.remove(img.path)
                    session.delete(img)
            session.delete(answer)

        # Удаляем задачу
        session.delete(task)
        session.commit()

        return {"status": "success", "task_id": task_id}
