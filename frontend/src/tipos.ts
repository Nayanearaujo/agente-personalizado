// Tipos do contrato da API (seção 5 da SPEC-parte3).

export interface Cores {
  principal: string;
  secundaria: string;
  destaque: string;
}

export interface ConfigPublica {
  nome: string;
  descricao: string;
  exemplos: string[];
  logo_url: string;
  cores: Cores;
  limites: { max_caracteres_pergunta: number };
  mensagem_nao_encontrado: string;
}

export interface Fonte {
  n: number;
  fonte: string;
  secao: string;
  trecho: string;
}

export type Papel = "usuario" | "assistente";

export interface Mensagem {
  papel: Papel;
  texto: string;
  fontes?: Fonte[];
  erro?: string;
  naoEncontrado?: boolean;
}

// Eventos que a rota /api/perguntar envia por SSE.
export type EventoSSE =
  | { tipo: "fontes"; fontes: Fonte[] }
  | { tipo: "texto"; delta: string }
  | { tipo: "fim"; naoEncontrado: boolean }
  | { tipo: "erro"; mensagem: string };
