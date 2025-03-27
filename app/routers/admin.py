from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import require_role
from app.schemas.user import UserOut, RoleUpdate
from app.models.user import User
from app.models.role import Role
from app.core.database import SessionLocal

router = APIRouter(prefix="/admin", tags=["admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    users = db.query(User).all()
    
    result = [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.name
        }       
        for user in users
    ]
    return result

@router.delete("/users/delete/{user_id}", status_code=200)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    user_to_delete = db.query(User).filter(User.id == user_id).first()

    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )

    # 🔒 Bloquer la suppression de soi-même
    if user_to_delete.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas vous supprimer vous-même."
        )

    # 🔒 Bloquer la suppression d'autres admins
    if user_to_delete.role.name == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas supprimer un autre administrateur."
        )

    db.delete(user_to_delete)
    db.commit()
    return {"detail": f"Utilisateur avec l'ID {user_id} supprimé avec succès."}

@router.put("/users/update/{user_id}/role")
def update_user_role(user_id: int, data: RoleUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # 🔒 Empêcher modification de son propre rôle
    if user.id == current_user.id:
        raise HTTPException(status_code=403, detail="Impossible de modifier votre propre rôle.")

    # 🔍 Chercher le rôle demandé
    role = db.query(Role).filter(Role.name == data.role_name).first()
    if not role:
        raise HTTPException(status_code=400, detail="Rôle invalide")

    user.role_id = role.id
    db.commit()
    db.refresh(user)

    return {"detail": f"Rôle de l'utilisateur '{user.username}' mis à jour en '{role.name}'."}