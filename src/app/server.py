from fastapi import FastAPI
from src.app.routes import router as router

app = FastAPI(
    title="API Monitoriza Ações",
    description="API para procurar cotações no Yahoo Finance e guardar em SQLite local.",
    version="1.0.0",
)

app.include_router(router)

# Rota de verificação de saúde da API (Health Check)
@app.get("/", tags=["Geral"])
def root():
    return {
        "mensagem": "A API está a correr em pleno!",
        "documentacao": "Aceda a http://127.0.0.1:8000/docs",
    }
