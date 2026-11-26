import html
import re
import unicodedata


_BLOCK_TAG_PATTERN = re.compile(
    r"</?(?:p|div|section|article|header|footer|h[1-6]|title|"
    r"ul|ol|table|thead|tbody|tr)\b[^>]*>",
    flags=re.IGNORECASE,
)
_LIST_ITEM_OPEN_PATTERN = re.compile(r"<li\b[^>]*>", flags=re.IGNORECASE)
_LIST_ITEM_CLOSE_PATTERN = re.compile(r"</li\s*>", flags=re.IGNORECASE)
_TAG_PATTERN = re.compile(r"<[^>]*>")
_SCRIPT_OR_STYLE_PATTERN = re.compile(
    r"<(?:script|style)\b[^>]*>.*?</(?:script|style)\s*>",
    flags=re.IGNORECASE | re.DOTALL,
)
_HTML_COMMENT_PATTERN = re.compile(r"<!--(.*?)-->", flags=re.DOTALL)


def preprocessar_texto(descricao_vaga: str) -> str:
    """Limpa tecnicamente uma descricao de vaga sem alterar seu significado."""
    if not isinstance(descricao_vaga, str):
        raise TypeError("descricao_vaga deve ser uma string.")

    texto = unicodedata.normalize("NFC", descricao_vaga)
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")

    texto = _HTML_COMMENT_PATTERN.sub(r"\1", texto)
    texto = _SCRIPT_OR_STYLE_PATTERN.sub("", texto)

    texto = re.sub(r"<br\s*/?>", "\n", texto, flags=re.IGNORECASE)
    texto = re.sub(r"<hr\s*/?>", "\n", texto, flags=re.IGNORECASE)
    texto = _BLOCK_TAG_PATTERN.sub("\n", texto)
    texto = _LIST_ITEM_OPEN_PATTERN.sub("\n- ", texto)
    texto = _LIST_ITEM_CLOSE_PATTERN.sub("\n", texto)
    texto = _TAG_PATTERN.sub("", texto)
    texto = html.unescape(texto)

    linhas_limpas = []
    for linha in texto.split("\n"):
        linha = re.sub(r"[^\S\n]+", " ", linha)
        linha = linha.strip()
        linhas_limpas.append(linha)

    texto = "\n".join(linhas_limpas)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()
