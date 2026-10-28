import { useState } from "react";
import type { Fonte } from "../tipos";

const EXTENSAO_PDF = /\.pdf$/i;

export default function CartaoFonte({ fonte }: { fonte: Fonte }) {
  const [aberto, setAberto] = useState(false);
  const ehPdf = EXTENSAO_PDF.test(fonte.fonte);

  return (
    <div className="rounded-xl border border-slate-200 bg-white text-left dark:border-slate-700 dark:bg-slate-800">
      <button
        type="button"
        onClick={() => setAberto((a) => !a)}
        aria-expanded={aberto}
        className="flex w-full items-center gap-2 px-3 py-2 text-sm"
      >
        <span className="flex h-5 w-5 flex-none items-center justify-center rounded-full bg-marca text-xs text-white">
          {fonte.n}
        </span>
        <span className="min-w-0 flex-1 truncate text-slate-700 dark:text-slate-200">
          {fonte.fonte} · {fonte.secao}
        </span>
        {ehPdf && (
          <span className="flex-none rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold text-slate-500 dark:bg-slate-700 dark:text-slate-300">
            PDF
          </span>
        )}
        <span className="flex-none text-slate-400">{aberto ? "▲" : "▼"}</span>
      </button>
      {aberto && (
        <p className="border-t border-slate-100 px-3 py-2 text-sm text-slate-600 dark:border-slate-700 dark:text-slate-300">
          {fonte.trecho}
        </p>
      )}
    </div>
  );
}
