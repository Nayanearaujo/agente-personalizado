"""Atualiza o endereço do Space sem criar outra conta ou expor credenciais."""

import os

from huggingface_hub import HfApi
from huggingface_hub.errors import HfHubHTTPError


def main():
    origem = os.environ.get("HF_ORIGEM", "").strip()
    usuario = os.environ.get("HF_USUARIO", "oaraujo").strip() or "oaraujo"
    destino = f"{usuario}/engenho-de-dados"
    if origem and "/" not in origem:
        origem = f"{usuario}/{origem}"
    api = HfApi(token=os.environ.get("HF_TOKEN"))
    escolhido = destino
    if origem and origem != destino:
        try:
            api.auth_check(destino, repo_type="space", write=True)
        except HfHubHTTPError:
            try:
                api.move_repo(from_id=origem, to_id=destino, repo_type="space")
                print(f"Space renomeado para {destino}.")
            except HfHubHTTPError as erro:
                codigo = getattr(getattr(erro, "response", None), "status_code", "?")
                print(f"::warning::Renomeação não concluída (HTTP {codigo}); publicando no Space existente.")
                escolhido = origem
    resumo = os.environ.get("GITHUB_STEP_SUMMARY")
    if resumo:
        with open(resumo, "a", encoding="utf-8") as f:
            f.write(f"\nSpace usado: https://huggingface.co/spaces/{escolhido}\n")
    with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as f:
        f.write(f"HF_SPACE={escolhido}\n")


if __name__ == "__main__":
    main()
