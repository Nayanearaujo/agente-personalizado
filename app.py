"""Chat educativo de chargeback com OpenRouter."""
import html
import os
from pathlib import Path

import gradio as gr
from openai import OpenAI
from validacao import carregar_config

RAIZ = Path(__file__).resolve().parent
CONFIG = carregar_config(RAIZ / "config.yml")

# O chat usa uma API externa. Esta função registra o suporte ao ZeroGPU
# exigido pelo ambiente da aula e não é chamada nas conversas.
if os.environ.get("SPACE_ID"):
    import spaces

    @spaces.GPU
    def _reserva_gpu():
        return None



def mensagem_erro(erro):
    codigo = getattr(erro, "status_code", None)
    return {
        401: "A chave do OpenRouter é inválida. Confira a configuração.",
        402: "O modelo exige créditos. Escolha um modelo gratuito na configuração.",
        403: "O provedor recusou o acesso. Confira as permissões no OpenRouter.",
        429: "O limite de uso foi atingido. Aguarde e tente novamente.",
    }.get(codigo, "Não foi possível consultar o modelo. Tente novamente em alguns instantes.")


def responder(mensagem, historico):
    chave = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not chave:
        yield "A chave do OpenRouter ainda não foi configurada. Cadastre OPENROUTER_API_KEY no ambiente."
        return
    mensagens = [{"role": "system", "content": CONFIG["prompt_sistema"]}]
    for item in historico:
        if item.get("role") in ("user", "assistant") and isinstance(item.get("content"), str):
            mensagens.append({"role": item["role"], "content": item["content"]})
    mensagens.append({"role": "user", "content": mensagem})
    resposta = ""
    fluxo = None
    try:
        with OpenAI(base_url="https://openrouter.ai/api/v1", api_key=chave,
                    timeout=60.0, max_retries=0) as cliente:
            fluxo = cliente.chat.completions.create(
                model=CONFIG["modelo"], messages=mensagens,
                max_tokens=CONFIG["max_tokens"], stream=True,
            )
            for evento in fluxo:
                if evento.choices:
                    trecho = evento.choices[0].delta.content
                    if trecho:
                        resposta += trecho
                        yield resposta
            if not resposta:
                yield "O modelo não retornou uma resposta. Tente novamente."
    except Exception as erro:
        aviso = mensagem_erro(erro)
        yield (resposta + "\n\nA resposta foi interrompida. " + aviso) if resposta else aviso
    finally:
        if fluxo is not None:
            fluxo.close()


def criar_interface():
    logo = CONFIG["logo"]
    if not logo.startswith("https://"):
        logo = "/gradio_api/file=" + str((RAIZ / logo).resolve())
    css = f"""
    .gradio-container {{background: #f3f5f3 !important; max-width: 1050px !important;}}
    #cabecalho {{background: {CONFIG['cor_principal']}; color: white; padding: 24px;
      border-radius: 16px; margin-bottom: 16px;}}
    #cabecalho h1, #cabecalho p {{color: white; margin: 0;}}
    #cabecalho img {{float: left; margin-right: 18px;}}
    #enviar {{background: {CONFIG['cor_secundaria']} !important; color: white !important;}}
    """
    with gr.Blocks(title=CONFIG["nome"], css=css, analytics_enabled=False) as pagina:
        gr.HTML(
            f'<header id="cabecalho"><img src="{html.escape(logo, quote=True)}" '
            f'width="{CONFIG["logo_tamanho"]}" height="{CONFIG["logo_tamanho"]}" alt="Logo">'
            f'<h1>{html.escape(CONFIG["nome"])}</h1><p>{html.escape(CONFIG["descricao"])}</p></header>'
        )
        gr.Markdown("Conteúdo educativo. Use exemplos fictícios e não envie dados pessoais ou de cartão.")
        conversa = gr.Chatbot(type="messages", label="Conversa", height=420)
        entrada = gr.Textbox(placeholder="Escreva sua dúvida sobre chargeback", label="Sua pergunta")
        enviar = gr.Button("Enviar", variant="primary", elem_id="enviar")
        parar = gr.Button("Parar resposta", variant="stop", visible=False)
        chat = gr.ChatInterface(
            responder, type="messages", chatbot=conversa, textbox=entrada,
            examples=CONFIG["exemplos"], submit_btn=enviar, stop_btn=parar,
            flagging_mode="never", save_history=False,
        )
        limpar = gr.Button("Limpar conversa")
        limpar.click(lambda: ([], "", [], []),
                     outputs=[conversa, entrada, chat.chatbot_state, chat.chatbot_value], queue=False)
    return pagina


if __name__ == "__main__":
    criar_interface().queue().launch(
        server_name=os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0" if os.environ.get("SPACE_ID") else "127.0.0.1"),
        server_port=int(os.environ.get("PORT", "7860")),
        allowed_paths=[str(RAIZ / "logo.svg")], share=False,
    )
