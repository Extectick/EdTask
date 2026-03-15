from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional, List
from data.data import Session, Task, Image, TaskImage, TaskFile, User

router = APIRouter(
    prefix="/master/task",
)


class CreateTaskSchema(BaseModel):
    title: str
    description: str
    master_token: str
    user_id: str  # Токен ученика, которому назначается задача
    image_ids: Optional[List[int]] = []  # Список ID изображений для привязки
    file_ids: Optional[List[int]] = []  # Список ID файлов для привязки (по умолчанию пустой)


@router.post("/create")
async def create(data: CreateTaskSchema):
    """Создаёт новое задание для конкретного ученика."""
    print(f"[DEBUG] create_task: title={data.title}, master_token={data.master_token}, user_id={data.user_id}")
    print(f"[DEBUG] image_ids type: {type(data.image_ids)}, value: {data.image_ids}")
    try:
        with Session() as session:
            # Мастер это пользователь с is_master=True
            master = session.query(User).filter(User.token == data.master_token, User.is_master == True).first()
            if not master:
                print(f"[DEBUG] Мастер не найден: {data.master_token}")
                raise HTTPException(status_code=404, detail="Master not found")

            # Проверяем что ученик существует и принадлежит этому мастеру
            student = session.query(User).filter(User.token == data.user_id, User.is_master == False, User.master_id == master.id).first()
            if not student:
                print(f"[DEBUG] Ученик не найден: {data.user_id}")
                raise HTTPException(status_code=404, detail="Student not found")

            new_task = Task(
                title=data.title,
                content=data.description,
                master_id=master.id,
                user_id=student.token  # Назначаем задачу ученику
            )
            session.add(new_task)
            session.commit()
            session.refresh(new_task)

            # Привязываем изображения к задаче через ID
            if data.image_ids:
                for image_id in data.image_ids:
                    task_image = TaskImage(task_id=new_task.id, image_id=image_id)
                    session.add(task_image)
            
            # Привязываем файлы к задаче через ID
            if data.file_ids:
                for file_id in data.file_ids:
                    task_file = TaskFile(task_id=new_task.id, file_id=file_id)
                    session.add(task_file)
            
            session.commit()

            print(f"[DEBUG] Задача создана: id={new_task.id}, user_id={new_task.user_id}")
            return {
                "status": "success",
                "task_id": new_task.id,
                "title": new_task.title,
                "description": new_task.content,
                "user_id": new_task.user_id
            }
    except Exception as e:
        print(f"[ERROR] create_task: {str(e)}")
        raise
