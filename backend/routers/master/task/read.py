from fastapi import HTTPException, APIRouter, Query
from data.data import Session, Task, TaskImage, TaskFile, Image, File, User, Answer

router = APIRouter(
    prefix="/master/task",
)


@router.get("")
async def get_tasks(
    master_token: str = Query(...),
    task_id: int = Query(None),
    user_id: str = Query(None),  # Токен ученика для фильтрации
    filter_status: str = Query(None, description="unreviewed | no_answers | in_revision | solved"),
    student_id: str = Query(None, description="Токен ученика для фильтрации ответов"),
):
    """Возвращает задачи мастера с поддержкой фильтрации."""
    with Session() as session:
        # Мастер это пользователь с is_master=True
        master = session.query(User).filter(User.token == master_token, User.is_master == True).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # ============================================
        # Режим 1: Получение задач для ученика (ученик видит только свои задачи)
        # ============================================
        if user_id:
            student = session.query(User).filter(User.token == user_id, User.is_master == False, User.master_id == master.id).first()
            if not student:
                raise HTTPException(status_code=404, detail="Student not found")

            # Получаем задачи назначенные этому ученику
            tasks = session.query(Task).filter(
                Task.user_id == student.token,
                Task.is_active == True
            ).all()

            result = []
            for task in tasks:
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

            return {"status": "success", "user_id": user_id, "tasks": result}

        # ============================================
        # Режим 2: Получение одной задачи по ID (мастер)
        # ============================================
        if task_id:
            task = session.query(Task).filter(Task.id == task_id, Task.master_id == master.id).first()
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            task_images = session.query(TaskImage).filter(TaskImage.task_id == task.id).all()
            images = []
            for ti in task_images:
                img = session.query(Image).filter(Image.id == ti.image_id).first()
                if img and img.path:
                    image_name = img.path.split('/')[-1].split('\\')[-1]
                    images.append({"id": img.id, "image_name": image_name})

            # Получаем файлы задачи
            task_files = session.query(TaskFile).filter(TaskFile.task_id == task.id).all()
            files = []
            for tf in task_files:
                file = session.query(File).filter(File.id == tf.file_id).first()
                if file and file.path:
                    file_name = file.path.split('/')[-1].split('\\')[-1]
                    files.append({"id": file.id, "file_name": file_name, "original_name": file.original_name or file_name})

            answers = session.query(Answer).filter(Answer.task_id == task.id).all()
            answers_data = []
            for answer in answers:
                answer_img = None
                if answer.image_id:
                    answer_img = session.query(Image).filter(Image.id == answer.image_id).first()
                
                image_data = None
                if answer_img and answer_img.path:
                    image_name = answer_img.path.split('/')[-1].split('\\')[-1]
                    image_data = {"id": answer_img.id, "image_name": image_name}
                
                answers_data.append({
                    "id": answer.id,
                    "task_id": answer.task_id,
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
                    "files": files,
                    "answers": answers_data,
                    "assigned_to": task.user_id  # Токен ученика
                }
            }

        # ============================================
        # Режим 3: Получение списка задач мастера с фильтрацией
        # ============================================
        # Базовый запрос — все задачи мастера
        query = session.query(Task).filter(Task.master_id == master.id)

        # Фильтр по student_id (токен ученика) — показывать только его задачи
        if student_id:
            student = session.query(User).filter(User.token == student_id, User.is_master == False, User.master_id == master.id).first()
            if not student:
                raise HTTPException(status_code=404, detail="Student not found")
            query = query.filter(Task.user_id == student.token)

        # Фильтр по статусу проверки
        if filter_status:
            if filter_status == "unreviewed":
                # Задачи, где есть хотя бы один ответ с comment_grade == 0 или NULL
                # И при этом нет ответов со статусом "Решено" (grade 2)
                unreviewed_subquery = session.query(Answer.task_id).filter(
                    (Answer.comment_grade == 0) | (Answer.comment_grade == None)
                ).distinct()
                solved_subquery = session.query(Answer.task_id).filter(
                    Answer.comment_grade == 2
                ).distinct()
                query = query.filter(
                    Task.id.in_(unreviewed_subquery),
                    Task.id.not_in(solved_subquery)
                )

            elif filter_status == "no_answers":
                # Задачи, у которых вообще нет ответов
                answer_subquery = session.query(Answer.task_id).distinct()
                query = query.filter(Task.id.not_in(answer_subquery))

            elif filter_status == "in_revision":
                # Задачи, где есть ответы со статусом 1 (на доработке)
                # И при этом нет ответов со статусом "Решено" (grade 2)
                revision_subquery = session.query(Answer.task_id).filter(
                    Answer.comment_grade == 1
                ).distinct()
                solved_subquery = session.query(Answer.task_id).filter(
                    Answer.comment_grade == 2
                ).distinct()
                query = query.filter(
                    Task.id.in_(revision_subquery),
                    Task.id.not_in(solved_subquery)
                )

            elif filter_status == "solved":
                # Задачи, где есть хотя бы один ответ со статусом 2 (решено)
                answer_subquery = session.query(Answer.task_id).filter(
                    Answer.comment_grade == 2
                ).distinct()
                query = query.filter(Task.id.in_(answer_subquery))

        tasks = query.all()

        # Формируем результат
        result = []
        for task in tasks:
            task_images = session.query(TaskImage).filter(TaskImage.task_id == task.id).all()
            images = []
            for ti in task_images:
                img = session.query(Image).filter(Image.id == ti.image_id).first()
                if img and img.path:
                    image_name = img.path.split('/')[-1].split('\\')[-1]
                    images.append({"id": img.id, "image_name": image_name})

            # Получаем файлы задачи
            task_files = session.query(TaskFile).filter(TaskFile.task_id == task.id).all()
            files = []
            for tf in task_files:
                file = session.query(File).filter(File.id == tf.file_id).first()
                if file and file.path:
                    file_name = file.path.split('/')[-1].split('\\')[-1]
                    files.append({"id": file.id, "file_name": file_name, "original_name": file.original_name or file_name})

            answers = session.query(Answer).filter(Answer.task_id == task.id).all()
            answers_data = []
            for answer in answers:
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

            # Получаем имя ученика
            student = session.query(User).filter(User.token == task.user_id).first()

            result.append({
                "id": task.id,
                "title": task.title,
                "description": task.content,
                "is_active": task.is_active,
                "created_at": str(task.created_at) if task.created_at else None,
                "images": images,
                "files": files,
                "answers_count": len(answers_data),
                "answers": answers_data,
                "assigned_to": task.user_id,
                "assigned_to_name": student.full_name if student else None
            })

        return {"status": "success", "master_id": master.id, "tasks": result, "count": len(result)}
