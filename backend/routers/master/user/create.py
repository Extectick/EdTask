from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from data.data import Session, User

router = APIRouter(
    prefix="/master/user/create",
)


class CreateUserSchema(BaseModel):
    user_id: str
    full_name: str
    master_token: str


@router.post("")
async def create_user(data: CreateUserSchema):
    """Создаёт нового пользователя (ученика)."""
    print(f"[DEBUG] Создание пользователя: user_id={data.user_id}, master_token={data.master_token}")
    with Session() as session:
        try:
            # Проверяем, нет ли уже такого пользователя
            existing = session.query(User).filter(User.token == data.user_id).first()
            if existing:
                print(f"[DEBUG] Пользователь уже существует: {data.user_id}")
                raise HTTPException(status_code=400, detail="User already exists")

            # Проверяем существование мастера по токену (мастер это пользователь с is_master=True)
            master = session.query(User).filter(User.token == data.master_token, User.is_master == True).first()
            if not master:
                print(f"[DEBUG] Мастер не найден: {data.master_token}")
                raise HTTPException(status_code=404, detail="Master not found")

            print(f"[DEBUG] Мастер найден: id={master.id}, token={master.token}")

            # Создаём нового пользователя (ученик с master_id)
            new_user = User(
                token=data.user_id,
                full_name=data.full_name,
                is_master=False,
                master_id=master.id
            )
            
            print(f"[DEBUG] Создаём пользователя: token={new_user.token}, master_id={new_user.master_id}")
            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            print(f"[DEBUG] Ученик создан: id={new_user.id}, token={new_user.token}, master_id={new_user.master_id}")
            return {
                "status": "success",
                "type": "user",
                "id": new_user.id,
                "user_id": new_user.token,
                "full_name": new_user.full_name,
                "master_id": master.id,
                "master_token": data.master_token
            }
        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Ошибка создания ученика: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Ошибка создания: {str(e)}")
