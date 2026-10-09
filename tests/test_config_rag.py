"""Contrato opcional da base, sem banco e sem chamadas ao provedor."""

import copy

import pytest
import yaml

from agente.config import ARQUIVO_PADRAO, RAIZ_PROJETO, carregar_config, validar


def test_base_desativada_enquanto_indexacao_nao_esta_pronta():
    base = carregar_config().base_conhecimento
    assert base.ativa is False
    assert base.tamanho_trecho == 1200
    assert base.sobreposicao == 150


def test_config_antiga_continua_valida():
    dados = yaml.safe_load(ARQUIVO_PADRAO.read_text())
    dados.pop("base_conhecimento")
    assert validar(dados, RAIZ_PROJETO) == []


@pytest.mark.parametrize("mudanca", [
    {"ativa": "false"}, {"sobreposicao": 1200},
    {"peso_palavras": 0, "peso_sentido": 0},
    {"peso_sentido": float("nan")}, {"peso_palavras": float("inf")},
    {"similaridade_minima": None}, {"tamanho_trecho": None},
    {"pasta": "../fora"}, {"pasta": "/tmp"},
    {"modelo_embedding": "outro"}, {"mensagem_nao_encontrado": "Não sei"},
])
def test_recusa_base_invalida(mudanca):
    dados = copy.deepcopy(yaml.safe_load(ARQUIVO_PADRAO.read_text()))
    dados["base_conhecimento"].update(mudanca)
    assert any("base_conhecimento" in erro for erro in validar(dados, RAIZ_PROJETO))


def test_recusa_link_que_sai_da_raiz(tmp_path):
    dados = yaml.safe_load(ARQUIVO_PADRAO.read_text())
    (tmp_path / "fora").symlink_to(RAIZ_PROJETO, target_is_directory=True)
    dados["base_conhecimento"]["pasta"] = "fora"
    assert any("caminho" in erro for erro in validar(dados, tmp_path))
