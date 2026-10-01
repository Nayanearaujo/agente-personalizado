"""Solicita a chave sem mostrá-la e inicia o chat local."""
import getpass
import os
import runpy
from pathlib import Path

if not os.environ.get("OPENROUTER_API_KEY"):
    chave = getpass.getpass("Cole sua chave do OpenRouter (ela ficará oculta): ").strip()
    if not chave:
        raise SystemExit("Nenhuma chave informada. Execute novamente para iniciar.")
    os.environ["OPENROUTER_API_KEY"] = chave

runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
