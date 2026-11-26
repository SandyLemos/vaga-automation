from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Identificacao(BaseSchema):
    cargo: Optional[str] = None
    empresa: Optional[str] = None
    localizacao: Optional[str] = None
    modalidade: Optional[str] = None
    tipo_contratacao: Optional[str] = None
    link_inscricao: Optional[str] = None


class Elegibilidade(BaseSchema):
    escolaridade: list[str] = Field(default_factory=list)
    formacao: list[str] = Field(default_factory=list)
    experiencia: list[str] = Field(default_factory=list)
    requisitos_obrigatorios: list[str] = Field(default_factory=list)
    requisitos_desejaveis: list[str] = Field(default_factory=list)
    conhecimentos_tecnicos: list[str] = Field(default_factory=list)
    outros_requisitos: list[str] = Field(default_factory=list)


class Condicoes(BaseSchema):
    salario: Optional[str] = None
    beneficios: list[str] = Field(default_factory=list)
    jornada: Optional[str] = None
    horario: Optional[str] = None
    duracao_contrato: Optional[str] = None


class Atividade(BaseSchema):
    atividade_original: str
    explicacao_pratica: str
    competencias_relacionadas: list[str] = Field(default_factory=list)


class ProcessoSeletivo(BaseSchema):
    etapas: list[str] = Field(default_factory=list)
    prazos: list[str] = Field(default_factory=list)
    observacoes: list[str] = Field(default_factory=list)


class RecursoGratuito(BaseSchema):
    nome: str
    descricao: str
    url: Optional[str] = None


class Preparacao(BaseSchema):
    assuntos_para_estudar: list[str] = Field(default_factory=list)
    recursos_gratuitos: list[RecursoGratuito] = Field(default_factory=list)
    exercicios_praticos: list[str] = Field(default_factory=list)


class CurriculoLinkedin(BaseSchema):
    competencias_para_destacar: list[str] = Field(default_factory=list)
    palavras_chave: list[str] = Field(default_factory=list)
    projetos_relevantes: list[str] = Field(default_factory=list)
    recomendacoes: list[str] = Field(default_factory=list)


class Entrevista(BaseSchema):
    perguntas_tecnicas: list[str] = Field(default_factory=list)
    perguntas_comportamentais: list[str] = Field(default_factory=list)


class VacancyAnalysis(BaseSchema):
    identificacao: Identificacao
    elegibilidade: Elegibilidade
    condicoes: Condicoes
    atividades: list[Atividade] = Field(default_factory=list)
    processo_seletivo: ProcessoSeletivo
    preparacao: Preparacao
    curriculo_linkedin: CurriculoLinkedin
    entrevista: Entrevista
    informacoes_ausentes: list[str] = Field(default_factory=list)
    observacoes_gerais: list[str] = Field(default_factory=list)
