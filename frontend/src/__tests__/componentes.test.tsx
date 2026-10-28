import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import Sugestoes from "../components/Sugestoes";
import CartaoFonte from "../components/CartaoFonte";
import CaixaPergunta from "../components/CaixaPergunta";
import Mensagem from "../components/Mensagem";
import type { ConfigPublica, Fonte } from "../tipos";

const config: ConfigPublica = {
  nome: "NOA Engenharia de Dados",
  descricao: "Tutora de dados.",
  exemplos: ["O que é RRF?", "O que é chunking?"],
  logo_url: "/api/logo",
  cores: { principal: "#123330", secundaria: "#0f2b28", destaque: "#ec8098" },
  limites: { max_caracteres_pergunta: 2000 },
  mensagem_nao_encontrado: "Não encontrei isso no material do curso.",
};

describe("Sugestoes", () => {
  it("mostra os exemplos e avisa quando um é escolhido", () => {
    const aoEscolher = vi.fn();
    render(<Sugestoes config={config} aoEscolher={aoEscolher} />);
    const botao = screen.getByText("O que é RRF?");
    fireEvent.click(botao);
    expect(aoEscolher).toHaveBeenCalledWith("O que é RRF?");
  });
});

describe("CartaoFonte", () => {
  const fonte: Fonte = { n: 1, fonte: "parte3-frontend-producao.pdf", secao: "10 Railway", trecho: "texto do trecho" };

  it("abre o trecho ao clicar e marca PDF", () => {
    render(<CartaoFonte fonte={fonte} />);
    expect(screen.getByText("PDF")).toBeInTheDocument();
    expect(screen.queryByText("texto do trecho")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button"));
    expect(screen.getByText("texto do trecho")).toBeInTheDocument();
  });
});

describe("CaixaPergunta", () => {
  it("envia ao clicar e não envia vazio", () => {
    const aoEnviar = vi.fn();
    render(<CaixaPergunta maxCaracteres={2000} ocupado={false} aoEnviar={aoEnviar} />);
    const botao = screen.getByText("Enviar");
    fireEvent.click(botao);
    expect(aoEnviar).not.toHaveBeenCalled();
    const area = screen.getByLabelText("Caixa de pergunta");
    fireEvent.change(area, { target: { value: "oi" } });
    fireEvent.click(botao);
    expect(aoEnviar).toHaveBeenCalledWith("oi");
  });
});

describe("Mensagem", () => {
  it("não mostra cartões quando a resposta é 'não encontrei'", () => {
    render(
      <Mensagem
        mensagem={{
          papel: "assistente",
          texto: "Não encontrei isso no material do curso.",
          fontes: [{ n: 1, fonte: "a.md", secao: "X", trecho: "y" }],
          naoEncontrado: true,
        }}
      />,
    );
    expect(screen.queryByText(/a\.md/)).not.toBeInTheDocument();
  });

  it("mostra cartões quando há fontes e a resposta é normal", () => {
    render(
      <Mensagem
        mensagem={{
          papel: "assistente",
          texto: "O RRF funde listas.",
          fontes: [{ n: 1, fonte: "parte2-rag.md", secao: "12 RRF", trecho: "trecho" }],
          naoEncontrado: false,
        }}
      />,
    );
    expect(screen.getByText(/parte2-rag\.md/)).toBeInTheDocument();
  });
});
