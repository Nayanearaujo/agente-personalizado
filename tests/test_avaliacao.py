import pytest

from agente.config import BaseConhecimento
from scripts.avaliar import calcular_metricas, ler_perguntas


def test_metricas_contam_erros_como_zero():
    hit, mrr = calcular_metricas([1, 2, None, 3])
    assert hit == 0.75
    assert mrr == pytest.approx((1 + 0.5 + 1 / 3) / 4)


def test_arquivo_de_perguntas_aponta_para_secoes_existentes():
    k, limiar, perguntas = ler_perguntas(BaseConhecimento())
    assert k == 3 and limiar == 0.85 and len(perguntas) == 8


def test_avaliacao_vazia_nao_aprova():
    with pytest.raises(ValueError):
        calcular_metricas([])
