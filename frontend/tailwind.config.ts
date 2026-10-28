import type { Config } from "tailwindcss";

// As cores da marca vêm do /api/config em tempo de execução (variáveis CSS),
// então aqui ficam só os ajustes gerais. O modo escuro usa a classe "dark".
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        marca: "var(--cor-principal)",
        "marca-secundaria": "var(--cor-secundaria)",
        destaque: "var(--cor-destaque)",
      },
      maxWidth: {
        leitura: "768px",
      },
    },
  },
  plugins: [],
} satisfies Config;
