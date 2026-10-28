"""Converte PDF para Markdown na indexação (nunca no servidor).

Usa pymupdf4llm, de licença AGPL. Por isso roda só no GitHub Actions, ao montar
o índice, e não vai para a imagem do servidor (fica no requirements-indexacao.txt).

A conversão limpa o que atrapalha a busca:
- cabeçalho e rodapé repetidos em muitas páginas;
- números de página soltos;
- negrito nos títulos e espaços repetidos.
E barra, com mensagem clara, um PDF escaneado (só imagem, sem texto).
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

MINIMO_CARACTERES = 200  # abaixo disso, tratamos como PDF escaneado


class PdfSemTexto(Exception):
    """O PDF não tem texto extraível (provavelmente escaneado)."""


def _paginas_markdown(caminho: Path) -> list[str]:
    import pymupdf4llm

    paginas = pymupdf4llm.to_markdown(str(caminho), page_chunks=True)
    # page_chunks devolve uma lista de dicts com a chave "text".
    return [p.get("text", "") if isinstance(p, dict) else str(p) for p in paginas]


def _linhas_repetidas(paginas: list[str]) -> set[str]:
    """Linhas curtas que aparecem em mais da metade das páginas (cabeçalho/rodapé)."""
    if len(paginas) < 3:
        return set()
    contagem: Counter[str] = Counter()
    for pagina in paginas:
        vistas = set()
        for linha in pagina.splitlines():
            texto = linha.strip()
            # Ignora linhas de tabela e linhas longas (conteúdo de verdade).
            if texto and len(texto) < 80 and not texto.startswith("|") and set(texto) != {"-"}:
                vistas.add(texto)
        contagem.update(vistas)
    limite = len(paginas) / 2
    return {linha for linha, n in contagem.items() if n > limite}


def _eh_numero_de_pagina(linha: str) -> bool:
    return bool(re.fullmatch(r"\s*\d{1,4}\s*", linha))


def _arrumar_titulo(linha: str) -> str:
    # Tira o negrito do título: '## **01 Texto**' -> '## 01 Texto'
    m = re.match(r"^(#{1,6})\s+(.*)$", linha)
    if not m:
        return linha
    nivel, texto = m.group(1), m.group(2).strip()
    texto = re.sub(r"\*\*(.+?)\*\*", r"\1", texto).strip()
    texto = re.sub(r"\s{2,}", " ", texto)
    if len(nivel) > 3:
        # Níveis 4 a 6 viram texto em negrito (legendas de diagrama, não seções).
        return f"**{texto}**"
    return f"{nivel} {texto}"


def limpar_paginas(paginas: list[str], nome: str) -> str:
    """Transforma as páginas (Markdown bruto) em um Markdown limpo.

    Separada de `pdf_para_markdown` para ser testável sem a biblioteca pymupdf4llm.
    Levanta PdfSemTexto se o conteúdo for pequeno demais (PDF escaneado).
    """
    texto_total = "".join(paginas).strip()
    vazias = sum(1 for p in paginas if len(p.strip()) < 10)
    if len(texto_total) < MINIMO_CARACTERES or (paginas and vazias > len(paginas) / 2):
        raise PdfSemTexto(
            f"❌ {nome} parece ser um PDF escaneado (só imagem): não há texto para extrair. "
            "Use um PDF com texto selecionável; OCR fica fora deste projeto."
        )
    repetidas = _linhas_repetidas(paginas)
    linhas_limpas: list[str] = []
    for pagina in paginas:
        for linha in pagina.splitlines():
            texto = linha.rstrip()
            despido = texto.strip()
            if not despido:
                linhas_limpas.append("")
                continue
            if despido in repetidas or _eh_numero_de_pagina(despido):
                continue
            if despido.startswith("#"):
                linhas_limpas.append(_arrumar_titulo(despido))
            else:
                linhas_limpas.append(texto)
    markdown = re.sub(r"\n{3,}", "\n\n", "\n".join(linhas_limpas)).strip()
    # Garante um título de documento (# ...). Se não houver, usa o nome do arquivo.
    if not re.search(r"^#\s+\S", markdown, re.MULTILINE):
        titulo = Path(nome).stem.replace("-", " ").replace("_", " ").strip().title()
        markdown = f"# {titulo}\n\n{markdown}"
    return markdown


def pdf_para_markdown(caminho: Path) -> str:
    """Lê um PDF e devolve Markdown limpo. Levanta PdfSemTexto se for escaneado."""
    return limpar_paginas(_paginas_markdown(caminho), caminho.name)
