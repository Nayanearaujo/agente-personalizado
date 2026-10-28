// Camada que fala com o servidor. Só caminhos relativos /api; nenhuma chave aqui.

import type { ConfigPublica, EventoSSE, Mensagem } from "./tipos";

export async function buscarConfig(): Promise<ConfigPublica> {
  const resposta = await fetch("/api/config");
  if (!resposta.ok) {
    throw new Error("Não foi possível carregar a configuração.");
  }
  return resposta.json();
}

export interface ErroPergunta {
  status: number;
  mensagem: string;
  tentarEm?: number;
}

/**
 * Envia a pergunta e devolve um gerador assíncrono de eventos SSE.
 * Quem chama vai consumindo os eventos (fontes, texto, fim, erro) e atualizando a tela.
 */
export async function* perguntar(
  mensagem: string,
  historico: Mensagem[],
  sinal?: AbortSignal,
): AsyncGenerator<EventoSSE> {
  const resposta = await fetch("/api/perguntar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mensagem,
      historico: historico.map((m) => ({ papel: m.papel, texto: m.texto })),
    }),
    signal: sinal,
  });

  if (!resposta.ok) {
    let corpo: { mensagem?: string; tentar_em?: number } = {};
    try {
      corpo = await resposta.json();
    } catch {
      corpo = {};
    }
    const erro: ErroPergunta = {
      status: resposta.status,
      mensagem: corpo.mensagem || "Não foi possível enviar a pergunta.",
      tentarEm: corpo.tentar_em,
    };
    throw erro;
  }

  if (!resposta.body) {
    throw { status: 0, mensagem: "Resposta vazia do servidor." } as ErroPergunta;
  }

  const leitor = resposta.body.getReader();
  const decodificador = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await leitor.read();
    if (done) break;
    buffer += decodificador.decode(value, { stream: true });
    const blocos = buffer.split("\n\n");
    buffer = blocos.pop() ?? "";
    for (const bloco of blocos) {
      const evento = analisarBloco(bloco);
      if (evento) yield evento;
    }
  }
}

function analisarBloco(bloco: string): EventoSSE | null {
  let nome = "";
  let dadoCru = "";
  for (const linha of bloco.split("\n")) {
    if (linha.startsWith("event: ")) nome = linha.slice(7).trim();
    else if (linha.startsWith("data: ")) dadoCru = linha.slice(6);
  }
  if (!nome || !dadoCru) return null;
  let dado: unknown;
  try {
    dado = JSON.parse(dadoCru);
  } catch {
    return null;
  }
  if (nome === "fontes") return { tipo: "fontes", fontes: dado as never };
  if (nome === "texto") return { tipo: "texto", delta: (dado as { delta: string }).delta };
  if (nome === "fim") return { tipo: "fim", naoEncontrado: (dado as { nao_encontrado: boolean }).nao_encontrado };
  if (nome === "erro") return { tipo: "erro", mensagem: (dado as { mensagem: string }).mensagem };
  return null;
}
