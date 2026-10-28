import { useEffect, useState } from "react";

// Lê a preferência salva; se não houver, segue o sistema.
function temaInicial(): "claro" | "escuro" {
  const salvo = localStorage.getItem("tema");
  if (salvo === "claro" || salvo === "escuro") return salvo;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "escuro" : "claro";
}

export default function AlternarTema() {
  const [tema, setTema] = useState<"claro" | "escuro">(temaInicial);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", tema === "escuro");
    localStorage.setItem("tema", tema);
  }, [tema]);

  return (
    <button
      type="button"
      onClick={() => setTema((t) => (t === "escuro" ? "claro" : "escuro"))}
      aria-label={tema === "escuro" ? "Mudar para modo claro" : "Mudar para modo escuro"}
      className="rounded-full p-2 text-white/90 transition hover:bg-white/10"
    >
      {tema === "escuro" ? "☀️" : "🌙"}
    </button>
  );
}
