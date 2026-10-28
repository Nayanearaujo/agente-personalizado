"""Servidor FastAPI: a API do assistente e a entrega da interface.

Substitui o app Gradio. As rotas /api expõem o mesmo "cérebro" das Partes 1 e 2
(busca no Supabase, prompt ancorado, troca automática de provedor), agora por HTTP.
A interface React compilada (frontend/dist) é servida pelo mesmo endereço.

Rodar no computador:
    uvicorn agente.servidor:app --reload --port 8000
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError

from agente.config import ErroConfig, carregar_config, validar_modo_gratuito
from agente.consulta import buscar_producao, conversar_com_base
from agente.limites import ErroLimite, LimitadorDeUso
from agente.provedores import criar_provedores

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("agente")

RAIZ = Path(__file__).resolve().parent.parent
PASTA_DIST = RAIZ / "frontend" / "dist"

# Prefixos de resposta do roteador que indicam erro (não ganham cartões de fonte).
PREFIXOS_ERRO = ("⚠️", "😕", "✋")


# ------------------------------------------------------------- inicialização

def _carregar():
    """Lê o config e monta a fila de provedores. Erro de config não derruba o /api/saude."""
    try:
        config = carregar_config()
        validar_modo_gratuito(config)
    except ErroConfig as erro:
        log.error("config.yaml inválido: %s", erro)
        return None, []
    provedores = criar_provedores(config)
    return config, provedores


CONFIG, PROVEDORES = _carregar()
LIMITADOR = LimitadorDeUso(
    por_minuto=int(os.environ.get("PERGUNTAS_POR_MINUTO", "10")),
    por_dia=int(os.environ.get("PERGUNTAS_POR_DIA", "100")),
)

app = FastAPI(title="NOA Engenharia de Dados", docs_url=None, redoc_url=None)


@app.middleware("http")
async def cabecalhos_de_seguranca(request: Request, call_next):
    resposta = await call_next(request)
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["Referrer-Policy"] = "same-origin"
    resposta.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; connect-src 'self'",
    )
    return resposta


# ------------------------------------------------------------------- helpers

def _versao() -> str:
    sha = os.environ.get("RAILWAY_GIT_COMMIT_SHA") or os.environ.get("SPACE_COMMIT") or ""
    return sha[:7] if sha else "local"


def ip_do_visitante(request: Request) -> str:
    encaminhado = request.headers.get("x-forwarded-for")
    if encaminhado:
        return encaminhado.split(",")[0].strip()
    return request.client.host if request.client else "desconhecido"


# ---------------------------------------------------------------- /api/saude

_cache_trechos: dict[str, float | int] = {"quando": 0.0, "valor": 0}


@app.get("/api/saude")
def saude():
    import time

    versao = _versao()
    if CONFIG is None:
        return JSONResponse({"status": "indisponivel", "versao": versao, "motivo": "config.yaml inválido"}, 503)
    if not CONFIG.base_conhecimento.ativa:
        return {"status": "ok", "versao": versao, "trechos_na_producao": 0}
    url = os.environ.get("SUPABASE_URL", "").strip()
    chave = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "").strip()
    if not url or not chave:
        return JSONResponse(
            {"status": "indisponivel", "versao": versao,
             "motivo": "faltam as variáveis SUPABASE_URL e SUPABASE_PUBLISHABLE_KEY"}, 503)
    # Conta os trechos, com cache de 60 s para não bater no banco a cada chamada.
    agora = time.monotonic()
    if agora - float(_cache_trechos["quando"]) > 60:
        try:
            from supabase import create_client

            resposta = create_client(url, chave).table("trechos").select(
                "id", count="exact").eq("colecao", "producao").limit(1).execute()
            _cache_trechos["valor"] = resposta.count or 0
            _cache_trechos["quando"] = agora
        except Exception:
            return JSONResponse(
                {"status": "indisponivel", "versao": versao,
                 "motivo": "a base de conhecimento está fora do ar"}, 503)
    return {"status": "ok", "versao": versao, "trechos_na_producao": _cache_trechos["valor"]}


# --------------------------------------------------------------- /api/config

@app.get("/api/config")
def config_publica():
    if CONFIG is None:
        return JSONResponse({"erro": "config_invalida"}, 503)
    return {
        "nome": CONFIG.nome,
        "descricao": CONFIG.descricao,
        "exemplos": CONFIG.exemplos,
        "logo_url": "/api/logo",
        "cores": {
            "principal": CONFIG.cor_principal,
            "secundaria": CONFIG.cor_secundaria,
            "destaque": CONFIG.cor_destaque,
        },
        "limites": {"max_caracteres_pergunta": CONFIG.max_caracteres_pergunta},
        "mensagem_nao_encontrado": CONFIG.base_conhecimento.mensagem_nao_encontrado,
    }


# ----------------------------------------------------------------- /api/logo

@app.get("/api/logo")
def logo():
    if CONFIG is None or not CONFIG.logo.is_file():
        return JSONResponse({"erro": "sem_logo"}, 404)
    tipos = {".png": "image/png", ".svg": "image/svg+xml", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
             ".webp": "image/webp"}
    tipo = tipos.get(CONFIG.logo.suffix.lower(), "application/octet-stream")
    return FileResponse(CONFIG.logo, media_type=tipo, headers={"Cache-Control": "public, max-age=3600"})


# ------------------------------------------------------------ /api/perguntar

class Mensagem(BaseModel):
    papel: str = Field(pattern="^(usuario|assistente)$")
    texto: str = Field(min_length=1, max_length=8000)

    model_config = {"extra": "forbid"}


class Pergunta(BaseModel):
    mensagem: str = Field(min_length=1)
    historico: list[Mensagem] = Field(default_factory=list, max_length=20)

    model_config = {"extra": "forbid"}


def _evento(nome: str, dados) -> str:
    return f"event: {nome}\ndata: {json.dumps(dados, ensure_ascii=False)}\n\n"


def _historico_para_roteador(historico: list[Mensagem]) -> list[dict]:
    """Converte {papel, texto} (API) para {role, content} (roteador interno)."""
    mapa = {"usuario": "user", "assistente": "assistant"}
    return [{"role": mapa[m.papel], "content": m.texto} for m in historico]


def eventos(pergunta: str, historico: list[Mensagem]):
    """Gera os eventos SSE a partir da resposta acumulada de conversar_com_base.

    O conversar_com_base devolve texto ACUMULADO e, no fim, cola a lista de fontes.
    Aqui separamos: buscamos os trechos uma vez (para o evento `fontes`) e emitimos
    o texto em pedaços (delta), terminando com `fim` ou `erro`.
    """
    base = CONFIG.base_conhecimento
    trechos = []
    if base.ativa:
        try:
            trechos = buscar_producao(pergunta, CONFIG) or []
        except Exception:
            yield _evento("erro", {"tipo": "base_indisponivel",
                                   "mensagem": "A base de conhecimento está indisponível. Tente mais tarde."})
            return
        if trechos:
            yield _evento("fontes", [
                {"n": i + 1, "fonte": t["fonte"], "secao": t["secao"], "trecho": t["conteudo"]}
                for i, t in enumerate(trechos)
            ])

    anterior = ""
    nao_encontrado = False
    houve_erro = None
    for acumulado in conversar_com_base(pergunta, _historico_para_roteador(historico), CONFIG, PROVEDORES,
                                        buscar=(lambda *_: trechos) if base.ativa else None):
        # conversar_com_base cola as fontes no fim; cortamos para não duplicar no SSE.
        texto = acumulado.split("\n\n**Fontes consultadas**")[0]
        if texto.startswith(PREFIXOS_ERRO):
            houve_erro = texto
            anterior = ""
            continue
        delta = texto[len(anterior):]
        if delta:
            yield _evento("texto", {"delta": delta})
        anterior = texto

    if houve_erro is not None:
        tipo = "sem_chave" if houve_erro.startswith("⚠️") else "provedores"
        yield _evento("erro", {"tipo": tipo, "mensagem": houve_erro})
        return
    if base.ativa and anterior.strip() == base.mensagem_nao_encontrado.strip():
        nao_encontrado = True
    yield _evento("fim", {"nao_encontrado": nao_encontrado})


@app.post("/api/perguntar")
async def perguntar(request: Request):
    if CONFIG is None:
        return JSONResponse({"erro": "config_invalida",
                             "mensagem": "O assistente está sem configuração válida."}, 503)
    corpo = await request.body()
    try:
        dados = Pergunta.model_validate_json(corpo)
    except ValidationError:
        return JSONResponse({"erro": "pedido_invalido",
                             "mensagem": "Pedido inválido. Envie 'mensagem' e, se quiser, 'historico'."}, 422)
    mensagem = dados.mensagem.strip()
    if not mensagem:
        return JSONResponse({"erro": "pedido_invalido", "mensagem": "A pergunta está vazia."}, 422)
    try:
        LIMITADOR.verificar_tamanho(mensagem, CONFIG.max_caracteres_pergunta)
        LIMITADOR.registrar(ip_do_visitante(request))
    except ErroLimite as erro:
        corpo_erro = {"erro": "pergunta_longa" if erro.status == 413 else "limite", "mensagem": erro.mensagem}
        cabecalhos = {}
        if erro.tentar_em is not None:
            corpo_erro["tentar_em"] = erro.tentar_em
            cabecalhos["Retry-After"] = str(erro.tentar_em)
        return JSONResponse(corpo_erro, erro.status, headers=cabecalhos)
    return StreamingResponse(eventos(mensagem, dados.historico), media_type="text/event-stream")


# ---------------------------------------------------------- a interface React

if PASTA_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=PASTA_DIST / "assets"), name="assets")

    @app.get("/{caminho:path}")
    def interface(caminho: str):
        # /api/... desconhecido vira 404 em JSON; o resto cai no index.html (SPA).
        if caminho.startswith("api/"):
            return JSONResponse({"erro": "nao_encontrado"}, 404)
        arquivo = PASTA_DIST / caminho
        if arquivo.is_file() and re.fullmatch(r"[\w\-./]+", caminho):
            return FileResponse(arquivo)
        return FileResponse(PASTA_DIST / "index.html")
