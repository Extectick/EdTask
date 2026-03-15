from fastapi import HTTPException, APIRouter, Form
from typing import Optional
from data.data import Session, Task, TaskImage, TaskFile, Image, File, User

router = APIRouter(
    prefix="/master/task",
)


@router.post("/update")
async def update(
    task_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    master_token: str = Form(...)
):
    """Обновляет задачу."""
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

        # Обновляем поля
        task.title = title
        task.content = description

        session.commit()
        session.refresh(task)

        return {
            "status": "success",
            "task_id": task.id,
            "title": task.title,
            "description": task.content
        }
