import type { ConfigPublica } from "../tipos";

// Tela inicial: logo, nome e os exemplos do config como cartões clicáveis.
export default function Sugestoes({
  config,
  aoEscolher,
}: {
  config: ConfigPublica;
  aoEscolher: (pergunta: string) => void;
}) {
  return (
    <div className="flex flex-col items-center gap-6 px-4 py-10 text-center">
      <img src={config.logo_url} alt="" className="h-20 w-20 rounded-2xl object-contain" />
      <div>
        <h2 className="bg-gradient-to-r from-marca to-destaque bg-clip-text text-2xl font-bold text-transparent">
          {config.nome}
        </h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{config.descricao}</p>
      </div>
      <div className="grid w-full max-w-leitura gap-2 sm:grid-cols-2">
        {config.exemplos.map((exemplo) => (
          <button
            key={exemplo}
            type="button"
            onClick={() => aoEscolher(exemplo)}
            className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-left text-sm text-slate-700 transition hover:border-destaque hover:shadow-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          >
            {exemplo}
          </button>
        ))}
      </div>
    </div>
  );
}
