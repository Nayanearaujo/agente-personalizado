import { useEffect, useRef } from "react";
import type { Mensagem as TipoMensagem } from "../tipos";
import Mensagem from "./Mensagem";

export default function Conversa({
  mensagens,
  pensando,
  aoTentarDeNovo,
}: {
  mensagens: TipoMensagem[];
  pensando: boolean;
  aoTentarDeNovo: () => void;
}) {
  const fim = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fim.current?.scrollIntoView({ behavior: "smooth" });
  }, [mensagens]);

  return (
    <div className="mx-auto flex w-full max-w-leitura flex-col gap-4 px-4 py-4">
      {mensagens.map((m, i) => (
        <Mensagem
          key={i}
          mensagem={m}
          pensando={pensando && i === mensagens.length - 1 && m.papel === "assistente"}
          aoTentarDeNovo={aoTentarDeNovo}
        />
      ))}
      <div ref={fim} />
    </div>
  );
}
