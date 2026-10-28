import { useRef, useState } from "react";

export default function CaixaPergunta({
  maxCaracteres,
  ocupado,
  aoEnviar,
}: {
  maxCaracteres: number;
  ocupado: boolean;
  aoEnviar: (texto: string) => void;
}) {
  const [texto, setTexto] = useState("");
  const area = useRef<HTMLTextAreaElement>(null);

  function enviar() {
    const limpo = texto.trim();
    if (!limpo || ocupado || limpo.length > maxCaracteres) return;
    aoEnviar(limpo);
    setTexto("");
    if (area.current) area.current.style.height = "auto";
  }

  function aoDigitar(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setTexto(e.target.value);
    // A caixa cresce com o texto.
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
  }

  function aoTeclar(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      enviar();
    }
  }

  const perto = texto.length > maxCaracteres * 0.8;
  const passou = texto.length > maxCaracteres;

  return (
    <div className="mx-auto w-full max-w-leitura px-4 pb-4">
      <div className="flex items-end gap-2 rounded-2xl border border-slate-300 bg-white p-2 dark:border-slate-600 dark:bg-slate-800">
        <textarea
          ref={area}
          value={texto}
          onChange={aoDigitar}
          onKeyDown={aoTeclar}
          rows={1}
          placeholder="Digite sua dúvida e pressione Enter…"
          aria-label="Caixa de pergunta"
          className="max-h-40 flex-1 resize-none bg-transparent px-2 py-1 text-slate-800 outline-none dark:text-slate-100"
        />
        <button
          type="button"
          onClick={enviar}
          disabled={ocupado || !texto.trim() || passou}
          className="rounded-full bg-destaque px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
        >
          Enviar
        </button>
      </div>
      {perto && (
        <p className={`mt-1 text-right text-xs ${passou ? "text-red-500" : "text-slate-400"}`}>
          {texto.length} / {maxCaracteres}
        </p>
      )}
    </div>
  );
}
