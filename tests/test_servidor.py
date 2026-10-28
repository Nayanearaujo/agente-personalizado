"""Contrato da API FastAPI, com busca e provedor simulados (sem rede, sem chave).

Confere: ordem dos eventos SSE, /api/config sem segredos, /api/saude,
e os erros 413, 422 e 429.
"""

import importlib

import pytest

fastapi_testclient = pytest.importorskip("fastapi.testclient")
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def cliente(monkeypatch):
    # Garante um ambiente limpo e recarrega o servidor com ele.
    for var in ("SUPABASE_URL", "SUPABASE_PUBLISHABLE_KEY", "OPENROUTER_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    import agente.servidor as servidor
    importlib.reload(servidor)
    return servidor, TestClient(servidor.app)


def _eventos(texto_sse):
    """Extrai a lista de (evento, dado-cru) de uma resposta text/event-stream."""
    blocos = [b for b in texto_sse.split("\n\n") if b.strip()]
    saida = []
    for bloco in blocos:
        nome = dado = None
        for linha in bloco.splitlines():
            if linha.startswith("event: "):
                nome = linha[len("event: "):]
            elif linha.startswith("data: "):
                dado = linha[len("data: "):]
        if nome:
            saida.append((nome, dado))
    return saida


def test_config_nao_vaza_segredo(cliente):
    _, client = cliente
    r = client.get("/api/config")
    assert r.status_code == 200
    corpo = r.json()
    assert "nome" in corpo and "cores" in corpo
    # Nada de prompt de sistema, modelo ou chave.
    texto = r.text.lower()
    for proibido in ("instrucoes", "instru\\u00e7", "prompt", "modelo", "openrouter", "temperatura", "sk-"):
        assert proibido not in texto


def test_saude_sem_supabase_da_503(cliente):
    _, client = cliente
    r = client.get("/api/saude")
    # base_conhecimento.ativa=true no config, mas sem as variáveis -> 503
    assert r.status_code == 503
    assert r.json()["status"] == "indisponivel"


def test_perguntar_vazia_da_422(cliente):
    _, client = cliente
    r = client.post("/api/perguntar", json={"mensagem": "   "})
    assert r.status_code == 422


def test_perguntar_campo_desconhecido_da_422(cliente):
    _, client = cliente
    r = client.post("/api/perguntar", json={"mensagem": "oi", "modelo": "gpt-4o"})
    assert r.status_code == 422


def test_perguntar_longa_da_413(cliente):
    servidor, client = cliente
    limite = servidor.CONFIG.max_caracteres_pergunta
    r = client.post("/api/perguntar", json={"mensagem": "a" * (limite + 1)})
    assert r.status_code == 413
    assert r.json()["erro"] == "pergunta_longa"


def test_eventos_em_ordem_com_simulacao(cliente, monkeypatch):
    servidor, client = cliente

    # Simula a busca (retorna um trecho) e a geração (texto acumulado).
    trechos = [{"fonte": "parte2-rag.md", "secao": "12 RRF", "conteudo": "O RRF funde listas."}]
    monkeypatch.setattr(servidor, "buscar_producao", lambda *a, **k: trechos)

    def fake_conversar(pergunta, historico, config, provedores, buscar=None):
        yield "O RRF "
        yield "O RRF funde as listas."

    monkeypatch.setattr(servidor, "conversar_com_base", fake_conversar)

    r = client.post("/api/perguntar", json={"mensagem": "o que é RRF?"})
    assert r.status_code == 200
    eventos = _eventos(r.text)
    nomes = [e[0] for e in eventos]
    assert nomes[0] == "fontes"
    assert "texto" in nomes
    assert nomes[-1] == "fim"


def test_limite_por_minuto_da_429(cliente, monkeypatch):
    servidor, client = cliente
    servidor.LIMITADOR.por_minuto = 2
    monkeypatch.setattr(servidor, "buscar_producao", lambda *a, **k: [])
    monkeypatch.setattr(servidor, "conversar_com_base",
                        lambda *a, **k: iter([servidor.CONFIG.base_conhecimento.mensagem_nao_encontrado]))
    for _ in range(2):
        client.post("/api/perguntar", json={"mensagem": "oi"})
    r = client.post("/api/perguntar", json={"mensagem": "oi"})
    assert r.status_code == 429
    assert "Retry-After" in r.headers
