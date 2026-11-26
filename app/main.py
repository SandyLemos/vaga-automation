from fastapi import FastAPI

from app.routes.vacancy import router as vacancy_router

app = FastAPI(
    title="VagaLens API",
    description="API para análise e preparação de candidatos para vagas de tecnologia.",
    version="1.0.0",
)

app.include_router(vacancy_router)


@app.get("/")
def home():
    return {"mensagem": "VagaLens API está funcionando!"}
