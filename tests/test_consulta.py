from agente.config import carregar_config
from agente.consulta import conversar_com_base


def test_sem_trechos_nao_chama_provedor():
    config = carregar_config()
    assert list(conversar_com_base("qual a capital?", [], config, [], buscar=lambda *_: [])) == [
        config.base_conhecimento.mensagem_nao_encontrado,
    ]


def test_erro_na_base_nao_finge_ausencia():
    def falha(*_):
        raise ValueError("segredo que não deve sair")

    texto = list(conversar_com_base("pergunta", [], carregar_config(), [], buscar=falha))[-1]
    assert "indisponível" in texto and "segredo" not in texto


def test_pergunta_longa_nao_consulta_banco():
    def nao_chamar(*_):
        raise AssertionError("Busca indevida")

    config = carregar_config()
    texto = list(conversar_com_base("a" * (config.max_caracteres_pergunta + 1), [], config, [], nao_chamar))
    assert "limite" in texto[-1]


def test_resposta_tem_fontes_dos_metadados(monkeypatch):
    def simular(pergunta, historico, config, provedores):
        assert "Documentos de consulta" in config.instrucoes
        yield "Resposta apoiada no material."

    monkeypatch.setattr("agente.consulta.responder", simular)
    fontes = [{"fonte": "a.md", "secao": "Vetores", "conteudo": "Vetor é uma lista."}]
    texto = list(conversar_com_base("o que é vetor?", [], carregar_config(), [], lambda *_: fontes))[-1]
    assert "Fontes consultadas" in texto and "a.md · Vetores" in texto


def test_falha_do_provedor_nao_ganha_fontes(monkeypatch):
    monkeypatch.setattr("agente.consulta.responder", lambda *_: iter(["😕 Não consegui responder agora."]))
    fontes = [{"fonte": "a.md", "secao": "A", "conteudo": "texto"}]
    texto = list(conversar_com_base("pergunta", [], carregar_config(), [], lambda *_: fontes))[-1]
    assert "Fontes consultadas" not in texto
