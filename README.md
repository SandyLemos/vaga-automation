# Vaga automation

Vaga automation é uma API para ajudar candidatos a compreender vagas de emprego, com foco em oportunidades na área de tecnologia. A aplicação recebe a descrição de uma vaga e usa o Gemini para organizar as informações, explicar atividades e sugerir formas de preparação.

## Como funciona

O fluxo principal é:

```text
n8n ou outro cliente
        ↓
FastAPI — POST /analisar-vaga
        ↓
Pré-processamento do texto
        ↓
Gemini — interpretação da vaga
        ↓
Validação com Pydantic
        ↓
Resposta JSON
```

O pré-processador faz uma limpeza técnica do texto antes de enviá-lo ao modelo. Ele normaliza quebras de linha e Unicode, reduz espaços em excesso, trata HTML simples e decodifica entidades HTML. Procura preservar o conteúdo relevante, incluindo links, emojis, datas, valores e listas; não classifica nem interpreta a vaga.

O Gemini é responsável pela análise. O resultado é convertido de JSON e validado com os modelos Pydantic antes de ser devolvido pela API. A integração também tenta modelos alternativos em caso de falhas de API.

## O que a análise pode retornar

A resposta estruturada inclui:

- Identificação da vaga, empresa, localização, modalidade e link de inscrição.
- Escolaridade, formação, experiência e requisitos.
- Salário, benefícios, jornada e horário.
- Atividades e explicações práticas.
- Etapas e prazos do processo seletivo.
- Sugestões de preparação, recursos gratuitos e exercícios.
- Recomendações para currículo, LinkedIn e entrevista.
- Informações ausentes e observações gerais.

Os campos sem informação no anúncio podem ser retornados como `null` ou listas vazias. Recomendações geradas pela IA não devem ser interpretadas como informações oficiais da empresa.

## Tecnologias

- Python
- FastAPI e Uvicorn
- Google Gemini (`google-genai`)
- Pydantic
- `python-dotenv`
- `re`, `html` e `unicodedata` da biblioteca padrão para o pré-processamento

## Estrutura do projeto

```text
app/
├── main.py                      # Criação da aplicação FastAPI
├── prompts/
│   └── vacancy_prompt.py        # Instruções de análise para o Gemini
├── routes/
│   └── vacancy.py               # Endpoint e modelos de entrada/saída da API
├── schemas/
│   └── vacancy_schema.py        # Estrutura validada da análise
└── services/
    ├── gemini_service.py        # Integração, tentativas e validação da resposta
    └── text_preprocessor.py     # Limpeza técnica da descrição da vaga
tests/
└── test_text_preprocessor.py    # Testes do pré-processador e da integração
requirements.txt                 # Dependências Python
.env.example                     # Exemplo de configuração local
```

## Requisitos

- Python compatível com as dependências do projeto.
- Uma chave de API do Google Gemini.

## Configuração e execução no Windows

No PowerShell, na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite `.env` e informe sua chave:

```dotenv
GEMINI_API_KEY=sua_chave_do_gemini
GEMINI_MODEL=gemini-3.8-flash
```

`GEMINI_MODEL` é opcional; se não for definido, o serviço usa `gemini-3.5-flash-lite` como modelo principal. A chave é necessária para iniciar a integração com o Gemini. Não publique nem versione o arquivo `.env`.

Inicie a API:

```powershell
python -m uvicorn app.main:app --reload
```

Por padrão, a API fica disponível em `http://127.0.0.1:8000`. A documentação interativa do FastAPI fica em `http://127.0.0.1:8000/docs`.

## Endpoints

### `GET /`

Verifica se a aplicação está respondendo. Exemplo de resposta:

```json
{
  "mensagem": "Vaga automation API está funcionando!"
}
```

### `POST /analisar-vaga`

Recebe um JSON com o campo `descricao_vaga`. A descrição deve conter pelo menos 20 caracteres.

Exemplo de requisição:

```json
{
  "descricao_vaga": "Vaga para Pessoa Desenvolvedora Python. Requisitos: experiência com APIs e conhecimento de FastAPI. Benefícios: vale-refeição."
}
```

Exemplo resumido do formato de resposta:

```json
{
  "modelo_utilizado": "nome-do-modelo",
  "analise": {
    "identificacao": {},
    "elegibilidade": {},
    "condicoes": {},
    "atividades": [],
    "processo_seletivo": {},
    "preparacao": {},
    "curriculo_linkedin": {},
    "entrevista": {},
    "informacoes_ausentes": [],
    "observacoes_gerais": []
  }
}
```

Os objetos internos seguem os campos definidos em `app/schemas/vacancy_schema.py`. Em caso de falha ao processar a análise, o endpoint retorna HTTP `502`.

## Testes

Com o ambiente virtual ativado:

```powershell
python -m unittest discover -s tests -v
```

Os testes cobrem normalização de espaços e quebras de linha, Unicode/HTML, listas, preservação de emojis e links, textos vazios, extração de JSON e uso do texto pré-processado no prompt.

## Integração com n8n

O n8n pode chamar `POST /analisar-vaga`, enviando a descrição no campo `descricao_vaga`. O pré-processamento e a análise são internos à API; o formato de entrada e a estrutura da resposta permanecem definidos pelo backend.

## 🚧 Em andamento

- Automação do fluxo com n8n.
- Testes e validação da integração.
- Documentação do projeto.
- Organização das evidências.
- Preparação dos materiais de entrega.

> Em breve, novas atualizações, evidências e materiais de entrega serão lançados.
