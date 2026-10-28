"""T23: o railway.json tem a configuração certa e nenhum segredo."""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def carregar():
    return json.loads((RAIZ / "railway.json").read_text(encoding="utf-8"))


def test_usa_o_dockerfile():
    cfg = carregar()
    assert cfg["build"]["builder"] == "DOCKERFILE"
    assert cfg["build"]["dockerfilePath"] == "Dockerfile"


def test_health_check_na_rota_de_saude():
    deploy = carregar()["deploy"]
    assert deploy["healthcheckPath"] == "/api/saude"
    assert deploy["healthcheckTimeout"] >= 120
    assert deploy["restartPolicyType"] == "ON_FAILURE"


def test_sem_segredo_no_railway_json():
    texto = (RAIZ / "railway.json").read_text(encoding="utf-8").lower()
    for proibido in ("sk-", "sb_secret", "api_key", "token", "password", "senha"):
        assert proibido not in texto


def test_dockerfile_nao_recebe_chave():
    texto = (RAIZ / "Dockerfile").read_text(encoding="utf-8")
    # Nenhuma chave como ARG/ENV (as chaves só existem nas Variables, em execução).
    for proibido in ("OPENROUTER_API_KEY", "SUPABASE_SECRET_KEY", "SUPABASE_PUBLISHABLE_KEY", "ANTHROPIC_API_KEY"):
        assert proibido not in texto
