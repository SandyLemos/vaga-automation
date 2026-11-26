import os

from dotenv import load_dotenv
from google import genai

# Carrega as variáveis do arquivo .env
load_dotenv()

# Recupera as configurações
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

# Verifica se as configurações existem
if not API_KEY or not MODEL:
    raise ValueError("Configure GEMINI_API_KEY e GEMINI_MODEL no .env")

# Cria o cliente Gemini
client = genai.Client(api_key=API_KEY)

# Envia uma solicitação simples
response = client.interactions.create(
    model=MODEL, input="Responda apenas com a palavra: CONECTADO"
)

# Exibe a resposta
print("Resposta do Gemini:")
print(response.output_text)
