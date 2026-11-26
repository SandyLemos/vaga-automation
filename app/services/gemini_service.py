import os
import random
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

from app.prompts.vacancy_prompt import SYSTEM_INSTRUCTION

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

if not API_KEY:
    raise ValueError("Configure GEMINI_API_KEY no .env")

MODELS_TO_TRY = list(
    dict.fromkeys(
        [
            PRIMARY_MODEL,
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite",
        ]
    )
)

client = genai.Client(api_key=API_KEY)


def gerar_com_resiliencia(prompt: str, max_tentativas: int = 2):
    ultimo_erro = None

    for model_name in MODELS_TO_TRY:
        for tentativa in range(1, max_tentativas + 1):
            try:
                response = client.interactions.create(
                    model=model_name,
                    input=prompt,
                )

                return model_name, response

            except errors.APIError as e:
                ultimo_erro = e

                if e.code in (429, 500, 502, 503, 504):
                    if tentativa < max_tentativas:
                        espera = (2 ** (tentativa - 1)) + random.uniform(0.2, 0.6)
                        print(
                            f"[{model_name}] Erro {e.code}. Nova tentativa em {espera:.1f}s."
                        )
                        time.sleep(espera)
                        continue

                print(f"[{model_name}] Erro {e.code}. Tentando próximo modelo.")
                break

    raise RuntimeError(
        "Nenhum modelo conseguiu processar a solicitação."
    ) from ultimo_erro


def analisar_vaga(descricao_vaga: str):
    prompt_completo = f"""
    {SYSTEM_INSTRUCTION}

    Agora analise a seguinte descrição de vaga:

    <DESCRICAO_DA_VAGA>
    {descricao_vaga}
    </DESCRICAO_DA_VAGA>

    Retorne somente o JSON solicitado nas instruções.
    """

    modelo_usado, response = gerar_com_resiliencia(prompt_completo)

    resultado = response.output_text

    if not resultado:
        raise ValueError("O Gemini não retornou um conteúdo textual.")

    return {"modelo_utilizado": modelo_usado, "analise": resultado}
