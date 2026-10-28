import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Mensagem as TipoMensagem } from "../tipos";
import CartaoFonte from "./CartaoFonte";
import Aviso from "./Aviso";

export default function Mensagem({
  mensagem,
  pensando,
  aoTentarDeNovo,
}: {
  mensagem: TipoMensagem;
  pensando?: boolean;
  aoTentarDeNovo?: () => void;
}) {
  const [copiado, setCopiado] = useState(false);

  if (mensagem.papel === "usuario") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-2xl bg-marca px-4 py-2 text-white">{mensagem.texto}</div>
      </div>
    );
  }

  // Resposta do assistente, à esquerda, sem balão, em Markdown.
  async function copiar() {
    await navigator.clipboard.writeText(mensagem.texto);
    setCopiado(true);
    setTimeout(() => setCopiado(false), 1500);
  }

  const mostrarCartoes = !mensagem.naoEncontrado && (mensagem.fontes?.length ?? 0) > 0;

  return (
    <div className="flex flex-col gap-2">
      {pensando && !mensagem.texto && (
        <p className="animate-pulse text-sm text-slate-400">Consultando o material…</p>
      )}
      {mensagem.texto && (
        <div className="group relative">
          <div className="prose prose-sm max-w-none text-slate-800 dark:prose-invert dark:text-slate-100">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{mensagem.texto}</ReactMarkdown>
          </div>
          <button
            type="button"
            onClick={copiar}
            aria-label="Copiar resposta"
            className="mt-1 text-xs text-slate-400 opacity-0 transition group-hover:opacity-100"
          >
            {copiado ? "Copiado ✓" : "Copiar"}
          </button>
        </div>
      )}
      {mostrarCartoes && (
        <div className="grid gap-2 sm:grid-cols-2">
          {mensagem.fontes!.map((f) => (
            <CartaoFonte key={f.n} fonte={f} />
          ))}
        </div>
      )}
      {mensagem.erro && <Aviso mensagem={mensagem.erro} aoTentarDeNovo={aoTentarDeNovo} />}
    </div>
  );
}
