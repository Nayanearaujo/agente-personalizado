"""Gera embeddings locais e grava somente teste, sem promover produção."""

import math
import os
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from agente.config import carregar_config  # noqa: E402
from agente.rag import Trecho, carregar_trechos  # noqa: E402


def ajustar_tokens(trechos, contar, limite=128, incluir_secao=False):
    """Subdivide preservando todo o texto, sem truncamento silencioso."""
    from hashlib import sha256

    saida = []
    introducoes = {}
    for trecho in trechos:
        chave_secao = (trecho.fonte, trecho.secao)
        if chave_secao not in introducoes:
            introducoes[chave_secao] = trecho.conteudo[:180].replace("\n", " ")
    for trecho in trechos:
        contexto = (
            f"Seção: {trecho.secao}\nIntrodução: {introducoes[(trecho.fonte, trecho.secao)]}\n"
            if incluir_secao else ""
        )
        pendentes = [trecho.conteudo]
        while pendentes:
            texto = pendentes.pop(0)
            if contar(contexto + texto) > limite:
                if len(texto) < 2:
                    raise ValueError("Um trecho não cabe no limite de tokens do modelo.")
                meio = len(texto) // 2
                pendentes[0:0] = [texto[:meio], texto[meio:]]
                continue
            chave = f"{trecho.id}\0{len(saida)}\0{texto}"
            saida.append(Trecho(
                "teste:" + sha256(chave.encode()).hexdigest(),
                trecho.fonte, trecho.secao, contexto + texto, len(saida),
            ))
    return saida


def preparar_linhas(trechos, vetores, versao):
    linhas = []
    for trecho, vetor in zip(trechos, vetores, strict=True):
        numeros = [float(v) for v in vetor]
        if len(numeros) != 384 or not all(math.isfinite(v) for v in numeros):
            raise ValueError("Embedding inválido: esperados 384 números finitos.")
        if not any(numeros):
            raise ValueError("Embedding inválido: vetor zero.")
        linhas.append({
            "id": trecho.id, "colecao": "teste", "versao": versao,
            "fonte": trecho.fonte, "secao": trecho.secao,
            "conteudo": trecho.conteudo, "embedding": numeros,
        })
    if not linhas:
        raise ValueError("Não há trechos para indexar.")
    return linhas


def main():
    url = os.environ.get("SUPABASE_URL", "").strip()
    chave = os.environ.get("SUPABASE_SECRET_KEY", "").strip()
    versao = os.environ.get("GITHUB_SHA", "").strip()
    if not url.startswith("https://") or not chave or not versao:
        print("Faltam SUPABASE_URL, SUPABASE_SECRET_KEY ou GITHUB_SHA para indexar.")
        return 1
    try:
        from fastembed import TextEmbedding
        from supabase import create_client
        from tokenizers import Tokenizer

        config = carregar_config().base_conhecimento
        trechos = carregar_trechos(RAIZ, config)
        modelo = TextEmbedding(model_name=config.modelo_embedding, threads=2)
        # Inicializa a sessão e obtém uma cópia independente do tokenizer.
        list(modelo.embed(["Inicialização"], batch_size=1))
        tokenizer = Tokenizer.from_str(modelo.model.tokenizer.to_str())
        tokenizer.no_truncation()
        tokenizer.no_padding()
        trechos = ajustar_tokens(
            trechos, lambda t: len(tokenizer.encode(t).ids), incluir_secao=True,
        )
        linhas = preparar_linhas(
            trechos, modelo.embed([t.conteudo for t in trechos], batch_size=16), versao,
        )
        banco = create_client(url, chave)
        # Somente depois de preparar TODOS os vetores alteramos teste.
        banco.table("trechos").delete().eq("colecao", "teste").execute()
        for inicio in range(0, len(linhas), 40):
            banco.table("trechos").insert(linhas[inicio:inicio + 40]).execute()
        resposta = banco.table("trechos").select("id", count="exact").eq(
            "colecao", "teste",
        ).eq("versao", versao).limit(1).execute()
        if resposta.count != len(linhas):
            raise ValueError("A contagem gravada não corresponde aos trechos preparados.")
        print(f"Coleção teste: {len(linhas)} trechos, 384 dimensões. Produção não foi alterada.")
        return 0
    except Exception as erro:
        # Não imprimir resposta HTTP nem traceback, que podem conter credenciais.
        codigo = getattr(erro, "code", None)
        seguro = codigo if isinstance(codigo, str) and codigo.isalnum() and len(codigo) < 12 else ""
        print(f"Indexação falhou ({type(erro).__name__} {seguro}). Confira banco, chaves e modelo.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
