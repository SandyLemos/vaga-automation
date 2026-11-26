from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import traceback

from app.services.gemini_service import analisar_vaga
from app.schemas.vacancy_schema import VacancyAnalysis

router = APIRouter()


class VacancyRequest(BaseModel):
    descricao_vaga: str = Field(
        min_length=20, description="Texto completo da descrição da vaga"
    )


class VacancyResponse(BaseModel):
    modelo_utilizado: str
    analise: VacancyAnalysis


@router.post("/analisar-vaga", response_model=VacancyResponse)
def analisar_vaga_endpoint(dados: VacancyRequest):

    try:
        resultado = analisar_vaga(dados.descricao_vaga)

        return resultado

    except Exception as erro:
        print(f"Erro ao analisar vaga: {erro}")
        traceback.print_exc()

        raise HTTPException(
            status_code=502, detail="Não foi possível processar a análise da vaga."
        )
