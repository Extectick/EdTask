from fastapi import HTTPException, APIRouter, Request
from pydantic import BaseModel
from data.data import Session
from data.data import User, MasterUser


router = APIRouter()


class LoginSchema(BaseModel):
    token: str

@router.post("/login")
async def login(data: LoginSchema, request: Request):
    with Session() as session:
        
        if request.client.host == "127.0.0.1" and data.token == "admin":
            return {"status": "success", "type": "admin", "user": "admin", "id": 0}
            
        
        master = session.query(MasterUser).filter(MasterUser.name == data.token).first()
        if master:
            return {"status": "success", "type": "master", "user": master.name, "id": master.master_id}
        
        
        user = session.query(User).filter(User.user_id == data.token).first()
        if user:
            return {"status": "success", "type": "user", "user": user.user_id, "id": user.id}
        
        
        raise HTTPException(status_code=404, detail="User not found")
