from app.services.gemini_service import analisar_vaga

descricao = """
Vaga: Analista de Suporte Técnico Jr.
Empresa: Omie

Responsabilidades:
- Prestar suporte técnico aos clientes.
- Investigar problemas relatados pelos usuários.
- Auxiliar na resolução de dúvidas sobre o sistema.

Requisitos:
- Conhecimentos básicos em informática.
- Boa comunicação.
- Capacidade de solucionar problemas.

Benefícios e salário: não informados.
"""

resultado = analisar_vaga(descricao)

print("\nModelo utilizado:")
print(resultado["modelo_utilizado"])

print("\nAnálise gerada:")
print(resultado["analise"])
