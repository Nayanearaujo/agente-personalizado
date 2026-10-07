"""O portão impede publicar um modelo pago por engano."""

from dataclasses import replace

import pytest

from agente.config import ErroConfig, Provedor, carregar_config, validar_modo_gratuito


def test_config_publicada_usa_somente_modelo_gratuito():
    validar_modo_gratuito(carregar_config())


@pytest.mark.parametrize("provedor,modelo", [("openrouter", "openai/gpt-4o"), ("openai", "gpt-5-mini")])
def test_config_paga_e_bloqueada(provedor, modelo):
    config = replace(carregar_config(), provedores=[Provedor(provedor, modelo)])
    with pytest.raises(ErroConfig, match="somente OpenRouter"):
        validar_modo_gratuito(config)
