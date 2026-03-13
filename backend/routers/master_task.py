from fastapi import HTTPException, APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from data.data import Session, Task, TaskImage, MasterUser, Answer, TaskAccessUser, TaskAccessRole, User, Role, Apprentice, UserRole
import os
import uuid
from datetime import datetime

router = APIRouter(
    prefix="/master/task",
)


class CreateTaskSchema(BaseModel):
    title: str
    description: str
    master_token: str


@router.post("/create")
async def create_task(data: CreateTaskSchema):
    """Создаёт новое задание."""
    print(f"[DEBUG] create_task: title={data.title}, master_token={data.master_token}")
    try:
        with Session() as session:
            # Проверяем существование мастера
            master = session.query(MasterUser).filter(MasterUser.name == data.master_token).first()
            if not master:
                print(f"[DEBUG] Мастер не найден: {data.master_token}")
                raise HTTPException(status_code=404, detail="Master not found")

            # Создаём задачу
            new_task = Task(
                title=data.title,
                description=data.description,
                teacher_id=master.master_id
            )
            session.add(new_task)
            session.commit()
            session.refresh(new_task)

            print(f"[DEBUG] Задача создана: id={new_task.id}")
            return {
                "status": "success",
                "task_id": new_task.id,
                "title": new_task.title,
                "description": new_task.description
            }
    except Exception as e:
        print(f"[ERROR] create_task: {str(e)}")
        raise


@router.post("/upload_image")
async def upload_image(
    task_id: int = Form(...),
    master_token: str = Form(...),
    image: UploadFile = File(...)
):
    """Загружает изображение и привязывает к задаче."""
    # Проверяем тип файла
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Проверяем существование задачи
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Проверяем, что задача принадлежит мастеру
        if task.teacher_id != master.master_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Генерируем уникальное имя файла
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Сохраняем файл
        file_path = os.path.join("data", "img", unique_filename)
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)

        # Создаём запись в БД
        task_image = TaskImage(
            task_id=task_id,
            image_name=unique_filename
        )
        session.add(task_image)
        session.commit()
        session.refresh(task_image)

        return {
            "status": "success",
            "image_id": task_image.id,
            "image_name": unique_filename,
            "file_path": file_path
        }


@router.post("/get_tasks")
async def get_tasks(master_token: str = Form(...)):
    """Возвращает все задачи мастера с изображениями и доступом."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Получаем все задачи мастера
        tasks = session.query(Task).filter(Task.teacher_id == master.master_id).all()

        result = []
        for task in tasks:
            # Получаем изображения задачи
            images = session.query(TaskImage).filter(TaskImage.task_id == task.id).all()
            
            # Получаем ответы
            answers = session.query(Answer).filter(Answer.task_id == task.id).all()
            answers_data = []
            for answer in answers:
                # Получаем изображения ответа
                answer_images = session.query(TaskImage).filter(TaskImage.answer_id == answer.id).all()
                answers_data.append({
                    "id": answer.id,
                    "user_id": answer.user_id,
                    "text": answer.text,
                    "created_at": str(answer.created_at) if answer.created_at else None,
                    "images": [{"id": img.id, "image_name": img.image_name} for img in answer_images]
                })
            
            # Получаем доступ
            access_users = session.query(TaskAccessUser).filter(TaskAccessUser.task_id == task.id).all()
            users_access = [{"user_id": au.user_id} for au in access_users]
            
            access_roles = session.query(TaskAccessRole).filter(TaskAccessRole.task_id == task.id).all()
            roles_access = [{"role_id": ar.role_id} for ar in access_roles]

            result.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_active": task.is_active,
                "created_at": str(task.created_at) if task.created_at else None,
                "images": [{"id": img.id, "image_name": img.image_name} for img in images],
                "answers": answers_data,
                "access": {
                    "users": users_access,
                    "roles": roles_access
                }
            })

        return {
            "status": "success",
            "master_id": master.master_id,
            "tasks": result
        }


@router.post("/delete_task")
async def delete_task(task_id: int = Form(...), master_token: str = Form(...)):
    """Удаляет задачу и все связанные данные."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Проверяем существование задачи
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Проверяем, что задача принадлежит мастеру
        if task.teacher_id != master.master_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Удаляем изображения задачи
        session.query(TaskImage).filter(TaskImage.task_id == task_id).delete()
        
        # Удаляем все ответы (изображения ответов удалятся каскадом или вручную)
        answers = session.query(Answer).filter(Answer.task_id == task_id).all()
        for answer in answers:
            session.query(TaskImage).filter(TaskImage.answer_id == answer.id).delete()
        session.query(Answer).filter(Answer.task_id == task_id).delete()
        
        # Удаляем задачу
        session.delete(task)
        session.commit()

        return {"status": "success", "task_id": task_id}


@router.post("/toggle_active")
async def toggle_active(task_id: int = Form(...), master_token: str = Form(...)):
    """Переключает статус активности задачи (active/inactive)."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Проверяем существование задачи
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Проверяем, что задача принадлежит мастеру
        if task.teacher_id != master.master_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Переключаем статус
        task.is_active = not task.is_active
        session.commit()
        session.refresh(task)

        return {
            "status": "success",
            "task_id": task_id,
            "is_active": task.is_active
        }


@router.post("/edit_task")
async def edit_task(
    task_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    master_token: str = Form(...)
):
    """Редактирует заголовок и описание задачи."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Проверяем существование задачи
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Проверяем, что задача принадлежит мастеру
        if task.teacher_id != master.master_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Обновляем данные
        task.title = title
        task.description = description
        session.commit()
        session.refresh(task)

        return {
            "status": "success",
            "task_id": task.id,
            "title": task.title,
            "description": task.description
        }


@router.post("/delete_image")
async def delete_image(
    task_id: int = Form(...),
    image_id: int = Form(...),
    master_token: str = Form(...)
):
    """Удаляет изображение задачи."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Проверяем существование задачи
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Проверяем, что задача принадлежит мастеру
        if task.teacher_id != master.master_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Находим изображение
        image = session.query(TaskImage).filter(
            TaskImage.id == image_id,
            TaskImage.task_id == task_id
        ).first()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        # Удаляем файл с диска
        file_path = os.path.join("data", "img", image.image_name)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Удаляем запись из БД
        session.delete(image)
        session.commit()

        return {"status": "success", "image_id": image_id}


@router.post("/get_access")
async def get_access(task_id: int = Form(...), master_token: str = Form(...)):
    """Возвращает список пользователей и ролей с доступом к задаче."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Проверяем существование задачи
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Проверяем, что задача принадлежит мастеру
        if task.teacher_id != master.master_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Получаем пользователей с доступом
        access_users = session.query(TaskAccessUser).filter(TaskAccessUser.task_id == task_id).all()
        users_list = []
        for au in access_users:
            user = session.query(User).filter(User.user_id == au.user_id).first()
            users_list.append({
                "id": au.id,
                "user_id": au.user_id,
                "full_name": user.full_name if user else None
            })

        # Получаем роли с доступом
        access_roles = session.query(TaskAccessRole).filter(TaskAccessRole.task_id == task_id).all()
        roles_list = []
        for ar in access_roles:
            role = session.query(Role).filter(Role.role_id == ar.role_id).first()
            roles_list.append({
                "id": ar.id,
                "role_id": ar.role_id,
                "role_name": role.role_name if role else None
            })

        return {
            "status": "success",
            "task_id": task_id,
            "users": users_list,
            "roles": roles_list
        }


@router.post("/grant_user_access")
async def grant_user_access(
    task_id: int = Form(...),
    user_id: str = Form(...),
    master_token: str = Form(...)
):
    """Даёт доступ пользователю к задаче."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Проверяем существование задачи
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Проверяем, что задача принадлежит мастеру
        if task.teacher_id != master.master_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Проверяем существование пользователя
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Проверяем, есть ли уже доступ
        existing = session.query(TaskAccessUser).filter(
            TaskAccessUser.task_id == task_id,
            TaskAccessUser.user_id == user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already has access")

        # Даём доступ
        access = TaskAccessUser(task_id=task_id, user_id=user_id)
        session.add(access)
        session.commit()

        return {"status": "success", "user_id": user_id}


@router.post("/grant_role_access")
async def grant_role_access(
    task_id: int = Form(...),
    role_id: str = Form(...),
    master_token: str = Form(...)
):
    """Даёт доступ роли к задаче."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Проверяем существование задачи
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Проверяем, что задача принадлежит мастеру
        if task.teacher_id != master.master_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Проверяем существование роли
        role = session.query(Role).filter(Role.role_id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        # Проверяем, есть ли уже доступ
        existing = session.query(TaskAccessRole).filter(
            TaskAccessRole.task_id == task_id,
            TaskAccessRole.role_id == role_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Role already has access")

        # Даём доступ
        access = TaskAccessRole(task_id=task_id, role_id=role_id)
        session.add(access)
        session.commit()

        return {"status": "success", "role_id": role_id}


@router.post("/revoke_user_access")
async def revoke_user_access(
    task_id: int = Form(...),
    access_id: int = Form(...),
    master_token: str = Form(...)
):
    """Отзывает доступ у пользователя."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Находим доступ
        access = session.query(TaskAccessUser).filter(
            TaskAccessUser.id == access_id,
            TaskAccessUser.task_id == task_id
        ).first()
        if not access:
            raise HTTPException(status_code=404, detail="Access not found")

        session.delete(access)
        session.commit()

        return {"status": "success", "access_id": access_id}


@router.post("/revoke_role_access")
async def revoke_role_access(
    task_id: int = Form(...),
    access_id: int = Form(...),
    master_token: str = Form(...)
):
    """Отзывает доступ у роли."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Находим доступ
        access = session.query(TaskAccessRole).filter(
            TaskAccessRole.id == access_id,
            TaskAccessRole.task_id == task_id
        ).first()
        if not access:
            raise HTTPException(status_code=404, detail="Access not found")

        session.delete(access)
        session.commit()

        return {"status": "success", "access_id": access_id}


# ============================================
# КЛИЕНТСКИЕ ЭНДПОИНТЫ (для учеников)
# ============================================

class ClientTaskSchema(BaseModel):
    user_id: str


@router.post("/client/get_tasks")
async def client_get_tasks(data: ClientTaskSchema):
    """Возвращает все доступные задачи для ученика."""
    with Session() as session:
        user = session.query(User).filter(User.user_id == data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_roles = session.query(UserRole).filter(UserRole.user_id == data.user_id).all()
        role_ids = [ur.role_id for ur in user_roles]
        
        access_users = session.query(TaskAccessUser).filter(TaskAccessUser.user_id == data.user_id).all()
        task_ids_from_users = [au.task_id for au in access_users]
        
        if role_ids:
            access_roles = session.query(TaskAccessRole).filter(TaskAccessRole.role_id.in_(role_ids)).all()
            task_ids_from_roles = [ar.task_id for ar in access_roles]
        else:
            task_ids_from_roles = []
        
        all_task_ids = set(task_ids_from_users + task_ids_from_roles)
        
        tasks = []
        for task_id in all_task_ids:
            task = session.query(Task).filter(Task.id == task_id, Task.is_active == True).first()
            if task:
                images = session.query(TaskImage).filter(TaskImage.task_id == task.id).all()
                
                user_answers = session.query(Answer).filter(
                    Answer.task_id == task_id,
                    Answer.user_id == data.user_id
                ).all()
                answers_data = []
                for answer in user_answers:
                    answer_images = session.query(TaskImage).filter(TaskImage.answer_id == answer.id).all()
                    answers_data.append({
                        "id": answer.id,
                        "text": answer.text,
                        "created_at": str(answer.created_at) if answer.created_at else None,
                        "images": [{"id": img.id, "image_name": img.image_name} for img in answer_images]
                    })
                
                tasks.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "created_at": str(task.created_at) if task.created_at else None,
                    "images": [{"id": img.id, "image_name": img.image_name} for img in images],
                    "my_answers": answers_data
                })
        
        tasks.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "status": "success",
            "user_id": data.user_id,
            "tasks": tasks
        }


@router.post("/client/submit_answer")
async def client_submit_answer(
    task_id: int = Form(...),
    user_id: str = Form(...),
    text: str = Form(...)
):
    """Добавляет ответ к задаче."""
    with Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        access_user = session.query(TaskAccessUser).filter(
            TaskAccessUser.task_id == task_id,
            TaskAccessUser.user_id == user_id
        ).first()
        
        if not access_user:
            user_roles = session.query(UserRole).filter(UserRole.user_id == user_id).all()
            role_ids = [ur.role_id for ur in user_roles]
            
            access_role = session.query(TaskAccessRole).filter(
                TaskAccessRole.task_id == task_id,
                TaskAccessRole.role_id.in_(role_ids)
            ).first()
            
            if not access_role:
                raise HTTPException(status_code=403, detail="No access to this task")
        
        answer = Answer(task_id=task_id, user_id=user_id, text=text)
        session.add(answer)
        session.commit()
        session.refresh(answer)
        
        return {
            "status": "success",
            "answer_id": answer.id,
            "task_id": task_id,
            "text": answer.text
        }


@router.post("/client/upload_answer_image")
async def client_upload_answer_image(
    task_id: int = Form(...),
    answer_id: int = Form(...),
    user_id: str = Form(...),
    image: UploadFile = File(...)
):
    """Загружает изображение к ответу."""
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    with Session() as session:
        answer = session.query(Answer).filter(
            Answer.id == answer_id,
            Answer.user_id == user_id
        ).first()
        if not answer:
            raise HTTPException(status_code=404, detail="Answer not found")
        
        if answer.task_id != task_id:
            raise HTTPException(status_code=400, detail="Answer does not belong to this task")
        
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        file_path = os.path.join("data", "img", unique_filename)
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        task_image = TaskImage(answer_id=answer_id, image_name=unique_filename)
        session.add(task_image)
        session.commit()
        session.refresh(task_image)
        
        return {
            "status": "success",
            "image_id": task_image.id,
            "image_name": unique_filename
        }
