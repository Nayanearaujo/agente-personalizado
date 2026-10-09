"""Fontes e conteúdo devem sobreviver à divisão, sem banco real."""

from dataclasses import replace

import pytest

from agente.config import BaseConhecimento
from agente.rag import carregar_trechos, dividir_documento, termos_lexicais


def test_sobreposicao_limite_e_ids_estaveis():
    config = replace(BaseConhecimento(), tamanho_trecho=200, sobreposicao=30)
    texto = "# Curso\n## Vetores\n" + "0123456789" * 57
    a = dividir_documento(texto, "curso.md", config)
    assert a == dividir_documento(texto, "curso.md", config)
    assert len({t.id for t in a}) == len(a)
    assert all(len(t.conteudo) <= 200 and t.secao == "Vetores" for t in a)
    assert a[0].conteudo[-30:] == a[1].conteudo[:30]
    reconstruido = a[0].conteudo + "".join(t.conteudo[30:] for t in a[1:])
    assert reconstruido == "0123456789" * 57


def test_secoes_nao_se_misturam():
    trechos = dividir_documento("# Curso\n## A\ntexto a\n## B\ntexto b", "a.md", BaseConhecimento())
    assert [(t.secao, t.conteudo) for t in trechos] == [("A", "texto a"), ("B", "texto b")]


@pytest.mark.parametrize("texto", ["", "sem título", "# Só título"])
def test_documento_invalido(texto):
    with pytest.raises(ValueError):
        dividir_documento(texto, "a.md", BaseConhecimento())


def test_recusa_arquivo_que_nao_e_markdown(tmp_path):
    pasta = tmp_path / "documentos"
    pasta.mkdir()
    (pasta / "a.pdf").write_bytes(b"PDF")
    with pytest.raises(ValueError, match="Markdown"):
        carregar_trechos(tmp_path, BaseConhecimento())


def test_lexical_prioriza_sigla_sem_mudar_pergunta_sem_siglas():
    assert termos_lexicais("Como funciona RRF no RAG? RRF?") == "RRF RAG"
    assert termos_lexicais("O que é sobreposição?") == "O que é sobreposição?"
