"""Limite de uso por visitante (IP): tamanho da pergunta e perguntas por minuto/dia.

Toda regra vale no servidor (RF58). A interface pode ajudar (contador, botão),
mas quem protege a chave de IA é esta verificação, por IP.

Guarda os horários das perguntas de cada IP em memória. Como o servidor roda
num contêiner só, isso basta para o nosso caso. Não guarda o texto das perguntas.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque


class ErroLimite(Exception):
    """Pergunta recusada por um limite. `status` é o código HTTP (413 ou 429)."""

    def __init__(self, status: int, mensagem: str, tentar_em: int | None = None):
        self.status = status
        self.mensagem = mensagem
        self.tentar_em = tentar_em
        super().__init__(mensagem)


class LimitadorDeUso:
    """Conta perguntas por IP numa janela de minuto e de dia."""

    def __init__(self, por_minuto: int = 10, por_dia: int = 100):
        self.por_minuto = por_minuto
        self.por_dia = por_dia
        self._historico: dict[str, deque[float]] = defaultdict(deque)
        self._trava = threading.Lock()

    def verificar_tamanho(self, mensagem: str, max_caracteres: int) -> None:
        """413 se a pergunta passar do limite de caracteres."""
        tamanho = len(mensagem)
        if tamanho > max_caracteres:
            raise ErroLimite(
                413,
                f"Sua pergunta tem {tamanho} caracteres e o limite é {max_caracteres}. "
                "Resuma um pouco ou divida em partes menores.",
            )

    def registrar(self, ip: str, agora: float | None = None) -> None:
        """Conta mais uma pergunta deste IP. 429 se passar do limite por minuto ou por dia."""
        agora = time.monotonic() if agora is None else agora
        with self._trava:
            marcas = self._historico[ip]
            # Remove o que já saiu da janela de 1 dia.
            limite_dia = agora - 86400
            while marcas and marcas[0] < limite_dia:
                marcas.popleft()
            no_minuto = sum(1 for t in marcas if t > agora - 60)
            no_dia = len(marcas)
            if no_minuto >= self.por_minuto:
                espera = 60 - int(agora - next(t for t in marcas if t > agora - 60))
                espera = max(1, espera)
                raise ErroLimite(
                    429,
                    f"Muitas perguntas seguidas. Tente de novo em {espera} segundos.",
                    tentar_em=espera,
                )
            if no_dia >= self.por_dia:
                raise ErroLimite(
                    429,
                    "Você atingiu o limite de perguntas de hoje. Tente novamente amanhã.",
                    tentar_em=86400,
                )
            marcas.append(agora)
