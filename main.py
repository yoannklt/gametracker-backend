from fastapi import FastAPI
from app.core.database import Base, engine
from app.routers import auth, users
from app.models import user, game

app = FastAPI()

# Crée les tables au démarrage (à remplacer par Alembic plus tard)
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur GameTracker API"}

app.include_router(auth.router)
app.include_router(users.router)