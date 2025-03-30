from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.schemas.user import UserOut
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role.name,
        "game_name": current_user.game_name if current_user.game_name != None else "",
        "tag_line": current_user.tag_line if current_user.tag_line != None else "",
        "region": current_user.region if current_user.region != None else ""
    }