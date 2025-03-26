from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    
class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    
    class Config: {
        "from_attribute": True
    }
    
class UserLogin(BaseModel):
    identifier: str # Mail ou Username
    password: str