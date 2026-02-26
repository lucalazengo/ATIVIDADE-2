from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import engine, Base
from routers import users, auth, models as models_router, videos as videos_router

# Import models to ensure they are registered with SQLAlchemy
from models import user, ml_model, video_analysis

# Cria as tabelas do Banco de Dados no carregamento (Idealmente seria usar Alembic em Prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vision Processing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # NEXT.js URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusao dos Routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticacao"])
app.include_router(users.router, prefix="/users", tags=["Usuarios (CRUD)"])
app.include_router(models_router.router, prefix="/models", tags=["Gerenciamento de Modelos ML"])
app.include_router(videos_router.router, prefix="/videos", tags=["Inferência e Video Processing"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Vision API Online"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

