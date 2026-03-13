from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from data.data import Session, User, Apprentice, MasterUser, UserRole, Role
from sqlalchemy.orm import selectinload


router = APIRouter(
    prefix="/master",
)


class CreateUserSchema(BaseModel):
    user_id: str
    full_name: str
    master_token: str


class CreateRoleSchema(BaseModel):
    role_id: str
    role_name: str
    master_token: str


class AssignRoleSchema(BaseModel):
    user_id: str
    role_id: str
    master_token: str


class DeleteRoleSchema(BaseModel):
    role_id: str
    master_token: str


class GetRolesSchema(BaseModel):
    master_token: str


class GetUsersSchema(BaseModel):
    master_token: str


class DeleteUserSchema(BaseModel):
    user_id: str
    master_token: str


@router.post("/new_user")
async def create_user(data: CreateUserSchema):
    print(f"[DEBUG] Создание пользователя: user_id={data.user_id}, master_token={data.master_token}")
    with Session() as session:
        # Проверяем, нет ли уже такого пользователя
        existing = session.query(User).filter(User.user_id == data.user_id).first()
        if existing:
            print(f"[DEBUG] Пользователь уже существует: {data.user_id}")
            raise HTTPException(status_code=400, detail="User already exists")

        # Проверяем существование мастера по токену
        master = session.query(MasterUser).filter(MasterUser.name == data.master_token).first()
        if not master:
            print(f"[DEBUG] Мастер не найден: {data.master_token}")
            raise HTTPException(status_code=404, detail="Master not found")

        # Создаём нового пользователя
        new_user = User(user_id=data.user_id, full_name=data.full_name)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Прикрепляем ученика к мастеру
        apprentice = Apprentice(user_id=data.user_id, master_id=master.master_id)
        session.add(apprentice)
        session.commit()

        print(f"[DEBUG] Ученик создан: id={new_user.id}")
        return {
            "status": "success",
            "type": "user",
            "id": new_user.id,
            "user_id": new_user.user_id,
            "full_name": new_user.full_name,
            "master_id": master.master_id,
            "master_token": data.master_token,
            "master_name": master.name,
            "master_full_name": master.full_name
        }


@router.post("/get_users")
async def get_users(data: GetUsersSchema):
    """Возвращает всех учеников мастера с их ролями."""
    print(f"[DEBUG] get_users вызван с master_token: {data.master_token}")
    with Session() as session:
        # Проверяем существование мастера по токену
        master = session.query(MasterUser).filter(MasterUser.name == data.master_token).first()
        if not master:
            print(f"[DEBUG] Мастер не найден: {data.master_token}")
            raise HTTPException(status_code=404, detail="Master not found")

        # Получаем всех учеников этого мастера
        apprentices = session.query(Apprentice).filter(Apprentice.master_id == master.master_id).all()
        print(f"[DEBUG] Найдено учеников: {len(apprentices)}")

        result = []
        for apprentice in apprentices:
            # Получаем данные пользователя
            user = session.query(User).filter(User.user_id == apprentice.user_id).first()

            # Получаем роли пользователя
            user_roles = session.query(UserRole).filter(UserRole.user_id == apprentice.user_id).all()
            roles = [ur.role_id for ur in user_roles]

            result.append({
                "id": user.id if user else None,
                "user_id": apprentice.user_id,
                "full_name": user.full_name if user else None,
                "roles": roles
            })

        print(f"[DEBUG] Возвращаем учеников: {result}")
        return {
            "status": "success",
            "master_id": master.master_id,
            "master_token": data.master_token,
            "users": result
        }


@router.post("/new_role")
async def create_role(data: CreateRoleSchema):
    """Создаёт новую роль."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == data.master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")
        
        # Проверяем, нет ли уже такой роли
        existing = session.query(Role).filter(Role.role_id == data.role_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Role already exists")
        
        # Создаём новую роль
        new_role = Role(role_id=data.role_id, role_name=data.role_name, master_id=master.master_id)
        session.add(new_role)
        session.commit()
        
        return {
            "status": "success",
            "role_id": new_role.role_id,
            "role_name": new_role.role_name,
            "master_id": master.master_id
        }


@router.post("/delete_role")
async def delete_role(data: DeleteRoleSchema):
    """Удаляет роль."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == data.master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")
        
        # Находим роль
        role = session.query(Role).filter(Role.role_id == data.role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Проверяем, что роль принадлежит мастеру
        if role.master_id != master.master_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        # Удаляем все назначения этой роли
        session.query(UserRole).filter(UserRole.role_id == data.role_id).delete()
        
        # Удаляем саму роль
        session.delete(role)
        session.commit()
        
        return {"status": "success", "role_id": data.role_id}


@router.post("/assign_role")
async def assign_role(data: AssignRoleSchema):
    """Назначает роль пользователю."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == data.master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")
        
        # Проверяем существование пользователя
        user = session.query(User).filter(User.user_id == data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Проверяем существование роли
        role = session.query(Role).filter(Role.role_id == data.role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Проверяем, что роль принадлежит мастеру
        if role.master_id != master.master_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        # Проверяем, нет ли уже такой роли у пользователя
        existing = session.query(UserRole).filter(
            UserRole.user_id == data.user_id,
            UserRole.role_id == data.role_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Role already assigned")
        
        # Назначаем роль
        user_role = UserRole(user_id=data.user_id, role_id=data.role_id)
        session.add(user_role)
        session.commit()
        
        return {
            "status": "success",
            "user_id": data.user_id,
            "role_id": data.role_id
        }


@router.post("/remove_role")
async def remove_role(data: AssignRoleSchema):
    """Удаляет роль у пользователя."""
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == data.master_token).first()
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")
        
        # Находим назначение роли
        user_role = session.query(UserRole).filter(
            UserRole.user_id == data.user_id,
            UserRole.role_id == data.role_id
        ).first()
        if not user_role:
            raise HTTPException(status_code=404, detail="Role assignment not found")
        
        # Проверяем, что роль принадлежит мастеру
        role = session.query(Role).filter(Role.role_id == data.role_id).first()
        if role and role.master_id != master.master_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        # Удаляем назначение
        session.delete(user_role)
        session.commit()
        
        return {"status": "success", "user_id": data.user_id, "role_id": data.role_id}


@router.post("/get_roles")
async def get_roles(data: GetRolesSchema):
    """Возвращает все роли мастера."""
    print(f"[DEBUG] get_roles вызван с master_token: {data.master_token}")
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == data.master_token).first()
        if not master:
            print(f"[DEBUG] Мастер не найден: {data.master_token}")
            raise HTTPException(status_code=404, detail="Master not found")

        # Получаем все роли мастера
        roles = session.query(Role).filter(Role.master_id == master.master_id).all()
        print(f"[DEBUG] Найдено ролей: {len(roles)}")

        roles_list = [
            {
                "role_id": role.role_id,
                "role_name": role.role_name
            }
            for role in roles
        ]

        return {
            "status": "success",
            "master_id": master.master_id,
            "roles": roles_list
        }


@router.post("/delete_user")
async def delete_user(data: DeleteUserSchema):
    """Удаляет пользователя и все связанные данные."""
    print(f"[DEBUG] delete_user вызван с user_id: {data.user_id}, master_token: {data.master_token}")
    with Session() as session:
        # Проверяем существование мастера
        master = session.query(MasterUser).filter(MasterUser.name == data.master_token).first()
        if not master:
            print(f"[DEBUG] Мастер не найден: {data.master_token}")
            raise HTTPException(status_code=404, detail="Master not found")

        # Проверяем существование пользователя
        user = session.query(User).filter(User.user_id == data.user_id).first()
        if not user:
            print(f"[DEBUG] Пользователь не найден: {data.user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        # Проверяем, что пользователь принадлежит этому мастеру
        apprentice = session.query(Apprentice).filter(
            Apprentice.user_id == data.user_id,
            Apprentice.master_id == master.master_id
        ).first()
        if not apprentice:
            print(f"[DEBUG] Пользователь не принадлежит этому мастеру")
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Удаляем все роли пользователя
        session.query(UserRole).filter(UserRole.user_id == data.user_id).delete()
        
        # Удаляем запись из Apprentice
        session.delete(apprentice)
        
        # Удаляем самого пользователя
        session.delete(user)
        session.commit()

        print(f"[DEBUG] Пользователь удалён: {data.user_id}")
        return {"status": "success", "user_id": data.user_id}
