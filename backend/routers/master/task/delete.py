from fastapi import HTTPException, APIRouter, Form
import os

from data.data import Answer, AnswerImage, File, Image, Session, Task, TaskFile, TaskImage, User
from media import delete_image

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

        task_images = session.query(TaskImage).filter(TaskImage.task_id == task_id).all()
        task_files = session.query(TaskFile).filter(TaskFile.task_id == task_id).all()
        answers = session.query(Answer).filter(Answer.task_id == task_id).all()

        image_ids_to_delete = {ti.image_id for ti in task_images}
        file_ids_to_delete = {tf.file_id for tf in task_files}

        for ti in task_images:
            session.delete(ti)

        for tf in task_files:
            session.delete(tf)

        for answer in answers:
            if answer.image_id:
                image_ids_to_delete.add(answer.image_id)

            answer_images = session.query(AnswerImage).filter(AnswerImage.answer_id == answer.id).all()
            for ai in answer_images:
                image_ids_to_delete.add(ai.image_id)
                session.delete(ai)
            session.delete(answer)

        session.flush()

        for image_id in image_ids_to_delete:
            img = session.query(Image).filter(Image.id == image_id).first()
            if img:
                delete_image(img.path)
                session.delete(img)

        for file_id in file_ids_to_delete:
            file = session.query(File).filter(File.id == file_id).first()
            if file and file.path:
                if os.path.exists(file.path):
                    os.remove(file.path)
                session.delete(file)

        # Удаляем задачу
        session.delete(task)
        session.commit()

        return {"status": "success", "task_id": task_id}
