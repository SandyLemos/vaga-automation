import json
from app.schemas.vacancy_schema import VacancyAnalysis
import os
import random
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

from app.prompts.vacancy_prompt import SYSTEM_INSTRUCTION
from app.services.text_preprocessor import preprocessar_texto

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


_ANALISE_ESTRUTURA = {
    "identificacao": ("dict", ["cargo", "empresa", "localizacao", "modalidade", "tipo_contratacao", "link_inscricao"]),
    "elegibilidade": ("dict", ["escolaridade", "formacao", "experiencia", "requisitos_obrigatorios", "requisitos_desejaveis", "conhecimentos_tecnicos", "outros_requisitos"]),
    "condicoes": ("dict", ["salario", "beneficios", "jornada", "horario", "duracao_contrato"]),
    "atividades": ("list", None),
    "processo_seletivo": ("dict", ["etapas", "prazos", "observacoes"]),
    "preparacao": ("dict", ["assuntos_para_estudar", "recursos_gratuitos", "exercicios_praticos"]),
    "curriculo_linkedin": ("dict", ["competencias_para_destacar", "palavras_chave", "projetos_relevantes", "recomendacoes"]),
    "entrevista": ("dict", ["perguntas_tecnicas", "perguntas_comportamentais"]),
    "informacoes_ausentes": ("list", None),
    "observacoes_gerais": ("list", None),
}

_LIST_FIELDS = {
    "identificacao": set(),
    "elegibilidade": {
        "escolaridade",
        "formacao",
        "experiencia",
        "requisitos_obrigatorios",
        "requisitos_desejaveis",
        "conhecimentos_tecnicos",
        "outros_requisitos",
    },
    "condicoes": {"beneficios"},
    "processo_seletivo": {"etapas", "prazos", "observacoes"},
    "preparacao": {"assuntos_para_estudar", "exercicios_praticos"},
    "curriculo_linkedin": {
        "competencias_para_destacar",
        "palavras_chave",
        "projetos_relevantes",
        "recomendacoes",
    },
    "entrevista": {"perguntas_tecnicas", "perguntas_comportamentais"},
}


def _extrair_objeto_json(resultado: str):
    texto = resultado.strip()
    bloco_codigo = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texto, re.DOTALL | re.IGNORECASE)
    if bloco_codigo:
        texto = bloco_codigo.group(1)
    else:
        inicio = texto.find("{")
        fim = texto.rfind("}")
        if inicio >= 0 and fim > inicio:
            texto = texto[inicio:fim + 1]

    return json.loads(texto)


def _normalizar_objeto(dados):
    if not isinstance(dados, dict):
        raise ValueError("A resposta do Gemini não contém um objeto JSON válido.")

    normalizado = {}
    for campo, (tipo, subcampos) in _ANALISE_ESTRUTURA.items():
        valor = dados.get(campo)

        if tipo == "dict":
            fonte = valor if isinstance(valor, dict) else {}
            secao = {}
            for subcampo in subcampos:
                subvalor = fonte.get(subcampo)
                if subcampo in _LIST_FIELDS[campo]:
                    secao[subcampo] = subvalor if isinstance(subvalor, list) else []
                else:
                    secao[subcampo] = subvalor
            normalizado[campo] = secao
        elif tipo == "list":
            normalizado[campo] = valor if isinstance(valor, list) else []

    if isinstance(normalizado["atividades"], list):
        normalizado["atividades"] = [
            {
                "atividade_original": atividade.get("atividade_original", ""),
                "explicacao_pratica": atividade.get("explicacao_pratica", ""),
                "competencias_relacionadas": (
                    atividade["competencias_relacionadas"]
                    if isinstance(atividade.get("competencias_relacionadas"), list)
                    else []
                ),
            }
            for atividade in normalizado["atividades"]
            if isinstance(atividade, dict)
        ]

    if isinstance(normalizado["preparacao"].get("recursos_gratuitos"), list):
        recursos = []
        for recurso in normalizado["preparacao"]["recursos_gratuitos"]:
            if isinstance(recurso, dict):
                recursos.append({
                    "nome": recurso.get("nome", ""),
                    "descricao": recurso.get("descricao", ""),
                    "url": recurso.get("url"),
                })
        normalizado["preparacao"]["recursos_gratuitos"] = recursos
    else:
        normalizado["preparacao"]["recursos_gratuitos"] = []

    return normalizado


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
    descricao_preprocessada = preprocessar_texto(descricao_vaga)

    prompt_completo = f"""
    {SYSTEM_INSTRUCTION}

    Analise a seguinte descrição de vaga:

    <DESCRICAO_DA_VAGA>
    {descricao_preprocessada}
    </DESCRICAO_DA_VAGA>

    Retorne somente o JSON solicitado nas instruções.
    """

    modelo_usado, response = gerar_com_resiliencia(prompt_completo)

    resultado = response.output_text

    if not resultado:
        raise ValueError("O Gemini não retornou conteúdo textual.")

    dados_json = _extrair_objeto_json(resultado)
    dados_json = _normalizar_objeto(dados_json)

    analise_validada = VacancyAnalysis.model_validate(dados_json)

    return {"modelo_utilizado": modelo_usado, "analise": analise_validada.model_dump()}
