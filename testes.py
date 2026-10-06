"""Portão T1 a T9, sem chamadas externas ou credenciais."""
import ast
from pathlib import Path
import re
import subprocess
import sys

from validacao import carregar_config, ConfiguracaoInvalida

RAIZ = Path(__file__).resolve().parent
PADROES = [
    re.compile(r"sk-or-v1-[A-Za-z0-9]{20,}"),
    re.compile(r"sk-(?:proj-|ant-api\d+-)?[A-Za-z0-9_-]{32,}"),
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"sb_secret_[A-Za-z0-9_-]{20,}"),
]


def arquivos_projeto():
    resultado = subprocess.run(["git", "ls-files", "-z"], cwd=RAIZ,
                               capture_output=True, check=False)
    if resultado.returncode == 0:
        return [RAIZ / p for p in resultado.stdout.decode().split("\0") if p]
    return [p for p in RAIZ.rglob("*") if p.is_file() and not any(
        parte in {".git", ".venv", "venv", "__pycache__"} for parte in p.relative_to(RAIZ).parts)]


def main():
    erros = []
    try:
        carregar_config(RAIZ / "config.yaml")
        print("T1 a T7: configuração aprovada.")
    except ConfiguracaoInvalida as erro:
        erros.extend(str(erro).splitlines())
    arquivos = arquivos_projeto()
    if not (RAIZ / "app.py").is_file():
        erros.append("T8: app.py não encontrado.")
    for arquivo in arquivos:
        if arquivo.suffix == ".py":
            try:
                ast.parse(arquivo.read_text(encoding="utf-8"), filename=str(arquivo))
            except (SyntaxError, UnicodeError, OSError):
                erros.append(f"T8: erro de sintaxe ou leitura em {arquivo.relative_to(RAIZ)}.")
        try:
            texto = arquivo.read_text(encoding="utf-8")
        except UnicodeError:
            continue
        except OSError:
            erros.append(f"T9: não foi possível verificar {arquivo.relative_to(RAIZ)}.")
            continue
        if any(p.search(texto) for p in PADROES):
            erros.append(f"T9: possível chave exposta em {arquivo.relative_to(RAIZ)}. Remova e revogue a chave.")
    if erros:
        print("Publicação bloqueada:")
        for erro in erros:
            print("-", erro)
        return 1
    print("T8: sintaxe aprovada.\nT9: nenhum padrão de chave exposta encontrado.")
    print("Portão aprovado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
