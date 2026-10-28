import type { ConfigPublica } from "../tipos";
import AlternarTema from "./AlternarTema";

export default function Cabecalho({
  config,
  aoNovaConversa,
}: {
  config: ConfigPublica;
  aoNovaConversa: () => void;
}) {
  return (
    <header className="bg-marca text-white">
      <div className="mx-auto flex max-w-leitura items-center gap-3 px-4 py-3">
        <img src={config.logo_url} alt={`Logo de ${config.nome}`} className="h-10 w-10 rounded-lg bg-white/10 object-contain" />
        <div className="min-w-0 flex-1">
          <h1 className="truncate text-lg font-bold">{config.nome}</h1>
          <p className="truncate text-xs text-white/70">{config.descricao}</p>
        </div>
        <button
          type="button"
          onClick={aoNovaConversa}
          className="rounded-full px-3 py-1 text-xs text-white/90 transition hover:bg-white/10"
        >
          Nova conversa
        </button>
        <AlternarTema />
      </div>
    </header>
  );
}
