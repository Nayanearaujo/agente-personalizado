import pytest

from agente.rag import Trecho
from scripts.indexar import ajustar_tokens, preparar_linhas


def test_subdivisao_preserva_conteudo_e_fontes():
    trecho = Trecho("teste:a", "a.md", "Seção A", "abcdef" * 50, 0)
    partes = ajustar_tokens([trecho], len, limite=128)
    assert "".join(t.conteudo for t in partes) == trecho.conteudo
    assert all(len(t.conteudo) <= 128 and t.secao == "Seção A" for t in partes)
    assert len(set(t.id for t in partes)) == len(partes)


@pytest.mark.parametrize("vetor", [[1] * 383, [float("nan")] * 384, [0] * 384])
def test_recusa_vetores_invalidos(vetor):
    with pytest.raises(ValueError):
        preparar_linhas([Trecho("a", "a.md", "A", "texto", 0)], [vetor], "sha")


def test_recusa_falta_de_vetor():
    with pytest.raises(ValueError):
        preparar_linhas([Trecho("a", "a.md", "A", "texto", 0)], [], "sha")


def test_cada_subtrecho_mantem_contexto_sem_estourar_limite():
    trecho = Trecho("a", "a.md", "RRF", "abcdef" * 50, 0)
    partes = ajustar_tokens([trecho], len, limite=256, incluir_secao=True)
    prefixo = "Seção: RRF\nIntrodução: " + trecho.conteudo[:180] + "\n"
    assert all(t.conteudo.startswith(prefixo) and len(t.conteudo) <= 256 for t in partes)
    assert "".join(t.conteudo.removeprefix(prefixo) for t in partes) == trecho.conteudo
