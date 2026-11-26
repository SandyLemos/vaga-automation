import os
import unittest
from unittest.mock import patch

os.environ.setdefault("GEMINI_API_KEY", "test-api-key")

from app.services.gemini_service import analisar_vaga
from app.services.text_preprocessor import preprocessar_texto
from app.services.gemini_service import _extrair_objeto_json, _normalizar_objeto


class TextPreprocessorTests(unittest.TestCase):
    def test_remove_espacos_duplicados_tabs_e_espacos_nas_linhas(self):
        texto = "  Desenvolvedor   Python\tBackend  \r\n  Modelo remoto "

        resultado = preprocessar_texto(texto)

        self.assertEqual(
            resultado,
            "Desenvolvedor Python Backend\nModelo remoto",
        )

    def test_normaliza_quebras_de_linha(self):
        resultado = preprocessar_texto("Titulo\r\nPrimeira linha\rSegunda linha")

        self.assertEqual(resultado, "Titulo\nPrimeira linha\nSegunda linha")
        self.assertNotIn("\r", resultado)

    def test_preserva_emoji_links_datas_salarios_e_percentuais(self):
        texto = (
            "🚀 Desenvolvedor Python\n"
            "Inscricao: https://empresa.com.br/vagas/123?tipo=backend\n"
            "Entrevista em 27/11/2026 às 14:30\n"
            "Salário: R$ 8.500,00 — bônus de 12%"
        )

        resultado = preprocessar_texto(texto)

        self.assertIn("🚀", resultado)
        self.assertIn("https://empresa.com.br/vagas/123?tipo=backend", resultado)
        self.assertIn("27/11/2026", resultado)
        self.assertIn("R$ 8.500,00", resultado)
        self.assertIn("12%", resultado)

    def test_decodifica_entidades_html(self):
        resultado = preprocessar_texto(
            "Pesquisa &amp; desenvolvimento&nbsp;&nbsp;&lt;Sênior&gt;"
        )

        self.assertEqual(
            resultado,
            "Pesquisa & desenvolvimento <Sênior>",
        )

    def test_mantem_listas_formatadas_e_titulos(self):
        texto = (
            "<h2>Requisitos</h2>"
            "<ul><li>Python</li><li>FastAPI</li></ul>"
            "<p>Atendimento 100% remoto</p>"
        )

        resultado = preprocessar_texto(texto)

        self.assertIn("Requisitos", resultado)
        self.assertIn("- Python", resultado)
        self.assertIn("- FastAPI", resultado)
        self.assertIn("Atendimento 100% remoto", resultado)

    def test_preserva_texto_e_nao_transforma_em_json(self):
        resultado = preprocessar_texto(
            "Comentário do anúncio:\nAtuar com APIs.\nNão remova esta informação."
        )

        self.assertEqual(
            resultado,
            "Comentário do anúncio:\nAtuar com APIs.\nNão remova esta informação.",
        )
        self.assertNotIn('"cargo"', resultado)

    def test_texto_vazio_ou_so_espacos_retorna_vazio(self):
        self.assertEqual(preprocessar_texto(""), "")
        self.assertEqual(preprocessar_texto(" \t\r\n  "), "")

    def test_unifica_sequencias_excessivas_de_linhas_em_branco(self):
        resultado = preprocessar_texto("Titulo\n\n\n\n\nBenefícios")

        self.assertEqual(resultado, "Titulo\n\nBenefícios")


class GeminiPreprocessingIntegrationTests(unittest.TestCase):
    def test_extrai_json_de_bloco_markdown(self):
        resultado = _extrair_objeto_json(
            "```json\n"
            '{"identificacao": {"cargo": "Analista"}}\n'
            "```"
        )

        self.assertEqual(resultado["identificacao"]["cargo"], "Analista")

    def test_normaliza_resposta_incompleta_sem_inventar_informacoes(self):
        resultado = _normalizar_objeto({
            "identificacao": {"cargo": "Analista"},
            "condicoes": {"beneficios": ["Vale-Refeição"]},
        })

        self.assertEqual(resultado["identificacao"]["cargo"], "Analista")
        self.assertEqual(resultado["condicoes"]["beneficios"], ["Vale-Refeição"])
        self.assertIsNone(resultado["identificacao"]["empresa"])
        self.assertEqual(resultado["atividades"], [])
        self.assertEqual(resultado["elegibilidade"]["requisitos_obrigatorios"], [])

    def test_usa_texto_preprocessado_no_prompt(self):
        response = type("Response", (), {"output_text": '{"ok": true}'})()

        with patch(
            "app.services.gemini_service.gerar_com_resiliencia",
            return_value=("gemini-test", response),
        ) as gerar:
            validado = type(
                "Validado",
                (),
                {"model_dump": lambda self: {"ok": True}},
            )()

            with patch(
                "app.services.gemini_service.VacancyAnalysis.model_validate",
                return_value=validado,
            ):
                analisar_vaga(
                    "<p>Vaga&nbsp;remota</p>\r\n<h2>Requisitos</h2>\r\nPython"
                )

        prompt_enviado = gerar.call_args.args[0]
        self.assertIn("Vaga remota", prompt_enviado)
        self.assertIn("Requisitos", prompt_enviado)


if __name__ == "__main__":
    unittest.main()
