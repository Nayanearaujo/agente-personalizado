---
title: NOA Engenharia de Dados
emoji: 🦉
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.28.0
python_version: "3.12"
app_file: app.py
short_description: Engenharia de Dados, estatística e machine learning
pinned: false
---

# NOA Engenharia de Dados

Um espaço para aprender Engenharia de Dados, estatística e machine learning em português. O assistente explica ideias, resolve exemplos com dados fictícios e ajuda a construir conhecimento, uma etapa por vez.

A estrutura foi adaptada do [projeto da aula](https://github.com/azrosolucoestecnologicas/agente-personalizado). O modelo principal é `google/gemma-4-31b-it:free`, no OpenRouter. O app recusa configurações com modelos pagos. O serviço gratuito continua sujeito a limites e disponibilidade.

## Personalizar

Edite `config.yaml` no GitHub e faça commit na `main`. Nome, cores, logo, instruções, exemplos e parâmetros ficam nesse arquivo. A logo fica em `assets/logo.png`. A publicação só começa depois que as verificações passam.

## Chaves

No Hugging Face, abra **Settings > Variables and secrets > New secret** e cadastre `OPENROUTER_API_KEY`. No GitHub, cadastre `HF_TOKEN` em **Settings > Secrets and variables > Actions > Secrets**, com escrita no seu Space. Não coloque chaves nos arquivos do projeto.

As variáveis `HF_USUARIO` e `HF_SPACE` do GitHub identificam o destino da publicação. O workflow tenta renomear o Space existente para `noa-engenharia-de-dados`. Se o token não permitir, publica no endereço anterior e registra um aviso no Summary. Depois de uma renomeação bem-sucedida, atualize `HF_SPACE` para `noa-engenharia-de-dados`.

## Rodar no computador

Use Python 3.12 e abra o terminal dentro da pasta que contém `app.py`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/perguntar.py --help
python app.py
```

No Windows, ative com `.venv\Scripts\Activate.ps1`. Configure `OPENROUTER_API_KEY` no ambiente antes de abrir o chat. Acesse http://127.0.0.1:7860. O chat abre sem chave, mas explica que ela precisa ser cadastrada para responder.

## Verificar antes de publicar

```bash
python scripts/validar_config.py
python scripts/procurar_chaves.py
python -m pytest -q
ruff check .
```

Os testes usam provedores simulados e não gastam créditos. Eles conferem a configuração, as mensagens, o histórico, a troca de provedor, os erros, a interface e a publicação. O app usa a estrutura de provedores da referência, mas esta configuração habilita somente OpenRouter gratuito.

## Arquivos

| Caminho | Função |
| --- | --- |
| `config.yaml` | Personalização do assistente |
| `app.py` | Inicialização e proteção contra modelos pagos |
| `agente/` | Configuração, interface, provedores, roteamento e erros |
| `assets/` | Logo |
| `scripts/` | Validação, busca de chaves, teste e publicação |
| `tests/` | Testes automáticos |
| `.github/workflows/` | Portão e publicação automática |

## Se uma consulta falhar

O chat mostra o provedor, o modelo e a causa, sem mostrar a chave. `401` indica chave inválida; `404` indica modelo ou rota indisponível; `429` indica limite de uso. Um erro de conexão é diferente de um modelo inexistente. Criar outra chave ou retirar o limite de gasto não garante a resolução dessas falhas.

## Próxima etapa

A Parte 1 publica e testa o assistente. A consulta aos documentos com RAG, Supabase e fontes será implementada na Parte 2. Por enquanto, o assistente não consulta apostilas nem executa código.
