"""Diferencia um modelo inexistente de uma restrição da conta."""

from agente.erros import traduzir


class Recusa(Exception):
    status_code = 404


def test_404_por_privacidade_explica_a_configuracao():
    motivo = traduzir(Recusa("No endpoints found matching your data policy"))
    assert "privacidade" in motivo
    assert "Privacy" in motivo


def test_404_por_indisponibilidade_nao_sugere_criar_chave():
    motivo = traduzir(Recusa("No endpoints found"))
    assert "nenhum provedor disponível" in motivo


def test_404_por_modelo_ausente_mantem_a_orientacao():
    motivo = traduzir(Recusa("model not found"))
    assert "confira o ID" in motivo
