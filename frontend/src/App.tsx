import { useEffect, useRef, useState } from "react";
import { buscarConfig, perguntar, type ErroPergunta } from "./api";
import type { ConfigPublica, Mensagem } from "./tipos";
import Cabecalho from "./components/Cabecalho";
import Sugestoes from "./components/Sugestoes";
import Conversa from "./components/Conversa";
import CaixaPergunta from "./components/CaixaPergunta";
import Aviso from "./components/Aviso";

export default function App() {
  const [config, setConfig] = useState<ConfigPublica | null>(null);
  const [erroConfig, setErroConfig] = useState<string | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [ocupado, setOcupado] = useState(false);
  const ultimaPergunta = useRef<string>("");

  useEffect(() => {
    buscarConfig()
      .then((c) => {
        setConfig(c);
        document.documentElement.style.setProperty("--cor-principal", c.cores.principal);
        document.documentElement.style.setProperty("--cor-secundaria", c.cores.secundaria);
        document.documentElement.style.setProperty("--cor-destaque", c.cores.destaque);
      })
      .catch(() => setErroConfig("Não foi possível carregar o assistente. Recarregue a página."));
  }, []);

  async function enviar(texto: string) {
    if (!config || ocupado) return;
    ultimaPergunta.current = texto;
    // Para a tela, guardamos tudo; para o servidor, só as mensagens com texto
    // de verdade (uma resposta vazia ou com erro não vira contexto, e a API
    // recusa texto vazio no histórico).
    const historico = mensagens.filter((m) => m.texto.trim() && !m.erro);
    setMensagens([...mensagens, { papel: "usuario", texto }, { papel: "assistente", texto: "" }]);
    setOcupado(true);

    const atualizarUltima = (parcial: Partial<Mensagem>) =>
      setMensagens((atual) => {
        const copia = [...atual];
        copia[copia.length - 1] = { ...copia[copia.length - 1], ...parcial };
        return copia;
      });

    try {
      let textoAcumulado = "";
      for await (const evento of perguntar(texto, historico)) {
        if (evento.tipo === "fontes") atualizarUltima({ fontes: evento.fontes });
        else if (evento.tipo === "texto") {
          textoAcumulado += evento.delta;
          atualizarUltima({ texto: textoAcumulado });
        } else if (evento.tipo === "fim") atualizarUltima({ naoEncontrado: evento.naoEncontrado });
        else if (evento.tipo === "erro") atualizarUltima({ erro: evento.mensagem });
      }
    } catch (e) {
      const erro = e as ErroPergunta;
      atualizarUltima({ erro: erro.mensagem || "Não foi possível responder. Tente de novo." });
    } finally {
      setOcupado(false);
    }
  }

  function novaConversa() {
    setMensagens([]);
  }

  function tentarDeNovo() {
    if (ultimaPergunta.current) {
      // Remove a última resposta com erro e refaz a pergunta.
      setMensagens((atual) => atual.slice(0, -2));
      const pergunta = ultimaPergunta.current;
      setTimeout(() => enviar(pergunta), 0);
    }
  }

  if (erroConfig) {
    return (
      <div className="flex h-full items-center justify-center p-6">
        <Aviso mensagem={erroConfig} aoTentarDeNovo={() => location.reload()} />
      </div>
    );
  }

  if (!config) {
    return <div className="flex h-full items-center justify-center text-slate-400">Carregando…</div>;
  }

  return (
    <div className="flex h-full flex-col bg-slate-50 dark:bg-slate-900">
      <Cabecalho config={config} aoNovaConversa={novaConversa} />
      <main className="flex-1 overflow-y-auto">
        {mensagens.length === 0 ? (
          <Sugestoes config={config} aoEscolher={enviar} />
        ) : (
          <Conversa mensagens={mensagens} pensando={ocupado} aoTentarDeNovo={tentarDeNovo} />
        )}
      </main>
      <CaixaPergunta
        maxCaracteres={config.limites.max_caracteres_pergunta}
        ocupado={ocupado}
        aoEnviar={enviar}
      />
    </div>
  );
}
