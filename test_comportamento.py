"""Verifica histórico, streaming e erros sem acessar o OpenRouter."""
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import app


class Cliente:
    argumentos = None
    eventos = []

    def __init__(self, **kwargs):
        self.chat = SimpleNamespace(completions=self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def create(self, **kwargs):
        Cliente.argumentos = kwargs
        def fluxo():
            for evento in Cliente.eventos:
                if isinstance(evento, Exception):
                    raise evento
                yield SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=evento))])
        return fluxo()


class Conversa(unittest.TestCase):
    def test_chave_ausente(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIn("ainda não foi configurada", list(app.responder("Oi", []))[0])

    def test_historico_e_streaming(self):
        Cliente.eventos = ["Olá", " mundo"]
        anterior = [{"role": "user", "content": "Antes"}, {"role": "assistant", "content": "Resposta"}]
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "valor-ficticio"}), patch.object(app, "OpenAI", Cliente):
            self.assertEqual(list(app.responder("Agora", anterior)), ["Olá", "Olá mundo"])
        self.assertEqual([m["role"] for m in Cliente.argumentos["messages"]], ["system", "user", "assistant", "user"])
        self.assertEqual(Cliente.argumentos["messages"][-1]["content"], "Agora")

    def test_falha_parcial_sem_expor_erro(self):
        Cliente.eventos = ["Início", RuntimeError("conteudo-privado")]
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "valor-ficticio"}), patch.object(app, "OpenAI", Cliente):
            saida = list(app.responder("Oi", []))[-1]
        self.assertIn("interrompida", saida)
        self.assertNotIn("conteudo-privado", saida)

    def test_interface(self):
        self.assertIsNotNone(app.criar_interface())


if __name__ == "__main__":
    unittest.main()
