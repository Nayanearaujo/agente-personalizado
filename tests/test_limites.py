"""Limites de uso por IP (tamanho, por minuto, por dia)."""

import pytest

from agente.limites import ErroLimite, LimitadorDeUso


def test_pergunta_longa_da_413():
    lim = LimitadorDeUso()
    with pytest.raises(ErroLimite) as exc:
        lim.verificar_tamanho("a" * 2001, 2000)
    assert exc.value.status == 413
    assert "2001" in exc.value.mensagem and "2000" in exc.value.mensagem


def test_tamanho_no_limite_passa():
    LimitadorDeUso().verificar_tamanho("a" * 2000, 2000)  # não levanta


def test_limite_por_minuto():
    lim = LimitadorDeUso(por_minuto=3, por_dia=100)
    agora = 1000.0
    for _ in range(3):
        lim.registrar("1.2.3.4", agora)
    with pytest.raises(ErroLimite) as exc:
        lim.registrar("1.2.3.4", agora)
    assert exc.value.status == 429
    assert exc.value.tentar_em and exc.value.tentar_em <= 60


def test_limite_por_dia():
    lim = LimitadorDeUso(por_minuto=1000, por_dia=5)
    # Espalha ao longo do dia para não bater no limite por minuto.
    for i in range(5):
        lim.registrar("9.9.9.9", 1000.0 + i * 120)
    with pytest.raises(ErroLimite) as exc:
        lim.registrar("9.9.9.9", 1000.0 + 5 * 120)
    assert exc.value.status == 429


def test_ips_sao_independentes():
    lim = LimitadorDeUso(por_minuto=2, por_dia=100)
    agora = 500.0
    lim.registrar("a", agora)
    lim.registrar("a", agora)
    # Outro IP não é afetado pelo limite do primeiro.
    lim.registrar("b", agora)
    lim.registrar("b", agora)
    with pytest.raises(ErroLimite):
        lim.registrar("a", agora)


def test_janela_do_minuto_desliza():
    lim = LimitadorDeUso(por_minuto=2, por_dia=100)
    lim.registrar("x", 0.0)
    lim.registrar("x", 1.0)
    # 61 s depois, as duas primeiras saíram da janela de 1 minuto.
    lim.registrar("x", 62.0)  # não levanta
