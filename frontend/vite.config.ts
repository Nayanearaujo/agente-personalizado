import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Em desenvolvimento, as chamadas /api vão para o servidor FastAPI na porta 8000.
// Em produção, o mesmo servidor entrega estes arquivos, então o caminho é relativo.
export default defineConfig({
  plugins: [react()],
  base: "/",
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/setupTests.ts"],
  },
});
