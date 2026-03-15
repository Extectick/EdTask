from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from data.data import Session, User

router = APIRouter(
    prefix="/master/students",
)


@router.get("")
async def get_students(master_token: str):
    """Возвращает список всех учеников мастера."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(User).filter(User.token == master_token, User.is_master == True).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Получаем всех учеников этого мастера
        students = session.query(User).filter(User.master_id == master.id, User.is_master == False).all()

        result = [
            {
                "id": student.id,
                "user_id": student.token,
                "full_name": student.full_name,
                "master_id": student.master_id,
            }
            for student in students
        ]

        return {
            "status": "success",
            "master_id": master.id,
            "students": result,
            "count": len(result)
        }
