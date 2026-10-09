"""Preparação de documentos para consulta, sem banco ou provedor nesta etapa."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

from agente.config import BaseConhecimento


@dataclass(frozen=True)
class Trecho:
    id: str
    fonte: str
    secao: str
    conteudo: str
    posicao: int


def dividir_documento(texto: str, fonte: str, config: BaseConhecimento) -> list[Trecho]:
    """Divide pelas seções e por caracteres. O tokenizer será aplicado na indexação."""
    if not texto.strip() or not re.search(r"^#\s+\S", texto, re.MULTILINE):
        raise ValueError(f"{fonte}: o documento precisa de título # e conteúdo.")
    tamanho, overlap = config.tamanho_trecho, config.sobreposicao
    if tamanho < 1 or not 0 <= overlap < tamanho:
        raise ValueError("O tamanho deve ser positivo e a sobreposição menor que ele.")
    secoes: list[tuple[str, str]] = []
    titulo, secao, linhas = "Introdução", "Introdução", []
    for linha in texto.splitlines():
        h = re.match(r"^(#{1,3})\s+(.+)$", linha)
        if h:
            if linhas:
                secoes.append((secao, "\n".join(linhas).strip()))
            nivel, nome = len(h[1]), h[2].strip()
            if nivel == 1:
                titulo = nome
            secao = titulo if nivel == 1 else nome
            linhas = []
        else:
            linhas.append(linha)
    secoes.append((secao, "\n".join(linhas).strip()))
    trechos = []
    for secao, conteudo in secoes:
        inicio = 0
        while inicio < len(conteudo):
            fim = min(inicio + tamanho, len(conteudo))
            parte = conteudo[inicio:fim]
            if parte.strip():
                posicao = len(trechos)
                chave = f"{fonte}\0{secao}\0{posicao}\0{parte}"
                trechos.append(Trecho(
                    "teste:" + sha256(chave.encode()).hexdigest(), fonte, secao, parte, posicao,
                ))
            if fim == len(conteudo):
                break
            inicio = fim - overlap
    if not trechos:
        raise ValueError(f"{fonte}: documento sem conteúdo além dos títulos.")
    return trechos


def carregar_trechos(raiz: Path, config: BaseConhecimento) -> list[Trecho]:
    pasta = (raiz / config.pasta).resolve()
    if not pasta.is_relative_to(raiz.resolve()) or not pasta.is_dir():
        raise ValueError("A pasta de documentos deve existir dentro do projeto.")
    arquivos = sorted(pasta.rglob("*"))
    trechos = []
    for arquivo in arquivos:
        if not arquivo.resolve().is_relative_to(pasta):
            raise ValueError("Os documentos não podem usar links para fora da pasta.")
        if arquivo.is_dir():
            continue
        if arquivo.suffix != ".md":
            raise ValueError(f"{arquivo.name}: nesta etapa somente Markdown .md é permitido.")
        trechos.extend(dividir_documento(
            arquivo.read_text(encoding="utf-8"), arquivo.relative_to(pasta).as_posix(), config,
        ))
    if not trechos:
        raise ValueError("A base precisa de pelo menos um documento com conteúdo.")
    return trechos
