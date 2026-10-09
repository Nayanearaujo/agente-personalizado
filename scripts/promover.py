"""Promoção ou restauração explícita, somente pelo servidor do Actions."""

import os
import sys


def main():
    try:
        from supabase import create_client

        banco = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"])
        funcao = "restaurar_colecao" if "--restaurar" in sys.argv else "promover_colecao"
        argumento = "p_versao_publicada" if funcao == "restaurar_colecao" else "p_versao"
        banco.rpc(funcao, {argumento: os.environ["GITHUB_SHA"]}).execute()
        print("Índice restaurado." if funcao == "restaurar_colecao" else "Índice aprovado promovido.")
        return 0
    except Exception as erro:
        print(f"Operação do índice falhou ({type(erro).__name__}). Produção precisa ser conferida.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
