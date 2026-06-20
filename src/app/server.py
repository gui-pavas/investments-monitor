from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.app.routes import router as router
from src.app.jobs.sync_job import start_jobs
from src.database.conn import db  # 1. Importamos a sua instância global do banco


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting application and background jobs...")

    # 2. Criamos as tabelas antes de ligar o agendador e a API
    try:
        db.setup_database("20260620010031_initial.sql")
        print("✅ Database tables checked/created successfully.")
    except Exception as e:
        print(f"❌ Error during database setup: {e}")

    start_jobs()
    yield
    print("🛑 Shutting down application...")


app = FastAPI(
    title="API Monitoriza Ações",
    description="API para procurar cotações no Yahoo Finance e guardar em SQLite local.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


# Health Check Route
@app.get("/", tags=["Geral"])
def root():
    return {
        "mensagem": "A API está a correr em pleno!",
        "documentacao": "Aceda a http://127.0.0.1:8000/docs",
    }
