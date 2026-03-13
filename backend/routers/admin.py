from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from data.data import Session, MasterUser, Apprentice, User
from sqlalchemy.orm import selectinload


router = APIRouter(
    prefix="/admin",
)


class CreateMasterSchema(BaseModel):
    name: str
    full_name: str


@router.post("/new_user")
async def create_master(data: CreateMasterSchema):
    with Session() as session:
        # Проверяем, нет ли уже такого мастера
        existing = session.query(MasterUser).filter(MasterUser.name == data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Master already exists")

        # Создаём нового мастера
        new_master = MasterUser(name=data.name, full_name=data.full_name)

        session.add(new_master)
        session.commit()
        session.refresh(new_master)

        return {"status": "success", "type": "master", "id": new_master.master_id, "name": new_master.name, "full_name": new_master.full_name}


@router.post("/get_masters")
async def get_masters():
    with Session() as session:
        masters = session.query(MasterUser).options(
            selectinload(MasterUser.apprentices)
        ).all()

        result = []
        for master in masters:
            apprentices_data = []
            for apprentice in master.apprentices:
                user = session.query(User).filter(User.user_id == apprentice.user_id).first()
                apprentices_data.append({
                    "id": apprentice.id,
                    "user_id": apprentice.user_id,
                    "full_name": user.full_name if user else None
                })

            result.append({
                "master_id": master.master_id,
                "name": master.name,
                "full_name": master.full_name,
                "apprentices": apprentices_data
            })

        return {"status": "success", "masters": result}
