from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.core.database import Base, engine
from app.models.role import Role
from app.routers import auth, admin, users, games
from app.models import user, game, role

app = FastAPI()

# Crée les tables au démarrage (à remplacer par Alembic plus tard)
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur GameTracker API"}

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(games.router)

def seed_roles():
    db = Session(bind=engine)
    existing_roles = db.query(Role).all()
    
    if not existing_roles:
        roles_to_create = [
            Role(id=1, name="admin", description="Administrateur du système"),
            Role(id=2, name="user", description="Utilisateur standard") 
        ]
        db.add_all(roles_to_create)
        db.commit()
        print("Rôles créés avec succès!")
    else:
        print("Les rôles existent déjà.")
        
seed_roles()