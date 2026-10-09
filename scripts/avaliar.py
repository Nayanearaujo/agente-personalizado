"""Avalia somente recuperação, sem chamar um provedor de geração."""

import os
from pathlib import Path
import sys

import yaml

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from agente.config import carregar_config  # noqa: E402
from agente.rag import carregar_trechos  # noqa: E402


def calcular_metricas(posicoes):
    if not posicoes:
        raise ValueError("A avaliação não pode ser vazia.")
    acertos = sum(p is not None for p in posicoes)
    return acertos / len(posicoes), sum(1 / p for p in posicoes if p is not None) / len(posicoes)


def ler_perguntas(config):
    dados = yaml.safe_load((RAIZ / "perguntas_teste.yml").read_text())
    k, limiar, perguntas = dados["top_k"], dados["limiar_hit_rate"], dados["perguntas"]
    if type(k) is not int or not 1 <= k <= 10:
        raise ValueError("top_k deve ser um inteiro de 1 a 10.")
    if isinstance(limiar, bool) or not isinstance(limiar, (int, float)) or not 0 < limiar <= 1:
        raise ValueError("limiar_hit_rate deve ser um número entre 0 e 1.")
    if not isinstance(perguntas, list) or not perguntas:
        raise ValueError("Escreva perguntas de teste.")
    fontes = {(t.fonte, t.secao) for t in carregar_trechos(RAIZ, config)}
    for p in perguntas:
        if not isinstance(p.get("pergunta"), str) or not p["pergunta"].strip():
            raise ValueError("Pergunta vazia ou inválida.")
        if (p["fonte_esperada"], p["secao_esperada"]) not in fontes:
            raise ValueError("Uma fonte ou seção esperada não existe nos documentos.")
    return k, limiar, perguntas


def main():
    try:
        from fastembed import TextEmbedding
        from supabase import create_client

        config = carregar_config().base_conhecimento
        k, limiar, perguntas = ler_perguntas(config)
        versao = os.environ["GITHUB_SHA"]
        banco = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"])
        versoes = banco.table("trechos").select("versao").eq("colecao", "teste").execute().data
        if not versoes or any(v["versao"] != versao for v in versoes):
            raise ValueError("O índice de teste não corresponde à versão avaliada.")
        modelo = TextEmbedding(model_name=config.modelo_embedding, threads=2)
        posicoes = []
        for pergunta in perguntas:
            vetor = next(modelo.embed([pergunta["pergunta"]])).tolist()
            resultados = banco.rpc("buscar_hibrido", {
                "p_texto": pergunta["pergunta"], "p_vetor": vetor,
                "p_colecao": "teste", "p_k": k,
                "p_peso_palavras": config.peso_palavras,
                "p_peso_sentido": config.peso_sentido,
                "p_sim_min": config.similaridade_minima,
            }).execute().data
            posicao = next((i for i, r in enumerate(resultados, 1)
                            if r["fonte"] == pergunta["fonte_esperada"]
                            and r["secao"] == pergunta["secao_esperada"]), None)
            posicoes.append(posicao)
            primeiro = resultados[0] if resultados else None
            fonte = f"{primeiro['fonte']} / {primeiro['secao']}" if primeiro else "nenhum resultado"
            print(f"{'OK' if posicao else 'ERRO'} posição={posicao}: {pergunta['pergunta']} | primeiro: {fonte}")
            if posicao is None:
                diagnostico = banco.rpc("buscar_hibrido", {
                    "p_texto": pergunta["pergunta"], "p_vetor": vetor,
                    "p_colecao": "teste", "p_k": 10,
                    "p_peso_palavras": config.peso_palavras,
                    "p_peso_sentido": config.peso_sentido, "p_sim_min": 0,
                }).execute().data
                for i, candidato in enumerate(diagnostico, 1):
                    print(f"Diagnóstico sem filtro {i}: {candidato['fonte']} / {candidato['secao']}")
        hit, mrr = calcular_metricas(posicoes)
        resumo = f"Hit rate@{k}: {hit:.3f} (mínimo {limiar}); MRR@{k}: {mrr:.3f}"
        print(resumo)
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
                f.write(resumo + "\n")
        if hit < limiar:
            print("Busca reprovada. Produção permanece intacta.")
            return 1
        print("Busca aprovada. A promoção será feita na etapa de publicação.")
        return 0
    except Exception as erro:
        print(f"Avaliação não concluída ({type(erro).__name__}). Confira configuração e banco.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
