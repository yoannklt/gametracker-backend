from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    
class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: str
    
    class Config: {
        "from_attribute": True
    }
    
class UserLogin(BaseModel):
    identifier: str # Mail ou Username
    password: str
    
class RoleUpdate(BaseModel):
    role_name: str
    
class RiotAccount(BaseModel):
    game_name: str
    tag_line: str
    region: str