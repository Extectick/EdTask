from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from data.data import Session, User

router = APIRouter(
    prefix="/master/user/delete",
)


class DeleteUserSchema(BaseModel):
    user_id: str
    master_token: str


@router.post("")
async def delete_user(data: DeleteUserSchema):
    """Удаляет пользователя и все связанные данные."""
    print(f"[DEBUG] delete_user: user_id={data.user_id}, master_token={data.master_token}")
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(User).filter(User.token == data.master_token, User.is_master == True).first()
        if not master:
            print(f"[DEBUG] Мастер не найден: {data.master_token}")
            raise HTTPException(status_code=404, detail="Master not found")

        # Проверяем существование пользователя
        user = session.query(User).filter(User.token == data.user_id).first()
        if not user:
            print(f"[DEBUG] Пользователь не найден: {data.user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        # Проверяем, что пользователь принадлежит этому мастеру
        if user.master_id != master.id:
            print(f"[DEBUG] Пользователь не принадлежит этому мастеру")
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Удаляем самого пользователя
        session.delete(user)
        session.commit()

        print(f"[DEBUG] Пользователь удалён: {data.user_id}")
        return {"status": "success", "user_id": data.user_id}
