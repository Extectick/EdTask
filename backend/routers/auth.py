from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from data.data import Session, User

router = APIRouter(
    prefix="/auth",
)


class LoginSchema(BaseModel):
    token: str


@router.post("/login")
async def login(data: LoginSchema):
    """Вход в аккаунт по токену."""
    with Session() as session:
        # Ищем пользователя по токену
        user = session.query(User).filter(User.token == data.token).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Определяем тип пользователя
        if user.is_master:
            user_type = "master"
        else:
            user_type = "student"

        return {
            "status": "success",
            "user": {
                "id": user.id,
                "token": user.token,
                "full_name": user.full_name,
                "is_master": user.is_master,
                "master_id": user.master_id,
                "type": user_type
            }
        }
