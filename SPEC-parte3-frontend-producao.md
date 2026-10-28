# SPEC — Parte 3: interface própria, PDF na base e deploy em produção

> Continuação das specs `SPEC-parte1-cicd-deploy.md` e `SPEC-parte2-rag.md`, que já estão implementadas e no ar.
> Esta spec diz **o que** construir e **como conferir**. O código vem depois, uma tarefa por vez (seção 12).
> Base: `aulas/chat/parte3/IDEIA.md` e a apostila "Parte 3: Front-end com IA e Produção".
> Adaptada à estrutura real deste repositório (NOA Engenharia de Dados), que difere da referência do curso nos nomes dos módulos e no modelo de embedding. As decisões são equivalentes às da aula; os nomes seguem o que já existe aqui.

**Decisões já tomadas com a aluna:**

| Pergunta | Decisão |
|---|---|
| Biblioteca da interface | **React + Vite + TypeScript + Tailwind**, compilada dentro da imagem e servida pelo mesmo servidor Python (**FastAPI**) |
| Onde publicar | **Estratégia Docker**: a mesma imagem roda no **Hugging Face (Space tipo Docker, gratuito)** e no **Railway**. O projeto é leve (embedding MiniLM de 384 dimensões, ~400 MB), então cabe no gratuito, diferente da referência do curso |
| Nome do serviço no Railway | `noa-engenharia-de-dados`, endereço `noa-engenharia-de-dados.up.railway.app` |
| Limites de uso | Por visitante (IP): **10 perguntas por minuto** e **100 por dia**; pergunta de até **2.000 caracteres** (o limite que já existe em `ia.max_caracteres_pergunta`) |
| Modelo de embedding | **MiniLM multilíngue, 384 dimensões** (sem mudança): continua o `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, com a coluna `vector(384)` do Supabase |
| Space do Hugging Face | Convertido de **Gradio** para **Docker** (não é pausado: passa a servir a interface nova, de graça). O Railway fica como segundo destino, com o mesmo Docker |
| PDF de teste | A apostila da Parte 3 (`documentos/parte3-frontend-producao.pdf`), que vira o próximo documento da base |

## Glossário rápido

| Termo | Em uma frase |
|---|---|
| **Front-end** | A parte que roda no navegador: o que a pessoa vê e clica. É pública: qualquer um lê o código dela. |
| **Back-end / servidor** | A parte que roda no servidor: busca no Supabase, guarda as chaves e chama a IA. |
| **API** | As "portas" do servidor (`/api/...`), cada uma com um contrato: o que recebe e o que devolve. |
| **SSE (Server-Sent Events)** | Uma resposta HTTP que fica aberta e vai recebendo pedaços, que é como a resposta aparece aos poucos. |
| **React / Vite / Tailwind** | Biblioteca de componentes de tela / ferramenta que compila o front-end / classes prontas de estilo. |
| **FastAPI** | Biblioteca Python para APIs. Valida a entrada sozinha (com Pydantic). |
| **Docker / imagem** | Receita (`Dockerfile`) que monta um pacote com sistema, Python, bibliotecas, modelo e código. Roda igual em qualquer lugar. |
| **Health check** | Rota (`/api/saude`) que a plataforma chama antes de trocar a versão. Se ela não responde, a versão antiga continua no ar. |
| **Rate limit (limite de uso)** | Quantas perguntas um visitante pode fazer por minuto e por dia. Passou disso, o servidor responde "aguarde" (429). |

---

## 1. Objetivo, escopo e o que fica fora

### 1.1 Objetivo
Dar ao assistente **cara de produto**:
- uma interface própria, moderna, com a logo e as cores do `config.yaml`;
- servida por uma API própria, no mesmo endereço;
- com o **mesmo portão** das Partes 1 e 2: nada vai para o ar sem passar nos testes e na avaliação da busca;
- com a base de conhecimento aceitando **PDF**, além de Markdown;
- rodando num contêiner **Docker**, que publica tanto no **Hugging Face (gratuito)** quanto no **Railway**, sem retrabalho.

### 1.2 O que entra na Parte 3
1. **Interface React** com: streaming; **cartões de fonte** clicáveis que mostram o trecho usado; sugestões na tela inicial; modo claro e escuro; funcionamento no celular; todos os estados resolvidos (vazio, pensando, erro, "não encontrei", limite de uso); tudo em português.
2. **Servidor FastAPI** com as rotas `/api/saude`, `/api/config`, `/api/logo` e `/api/perguntar`. É o mesmo servidor que entrega a interface, num **único endereço**.
3. **Limites de uso no servidor**: 413 para pergunta grande demais e 429 para perguntas demais, com tempo de espera.
4. **PDF em `documentos/`**, convertido para Markdown na indexação, sem cabeçalhos, rodapés e números de página repetidos. PDF escaneado é barrado com mensagem clara.
5. **Docker** em dois estágios (Node compila a interface; Python roda o servidor com o modelo dentro da imagem).
6. **`railway.json`** no repositório: a configuração do Railway versionada.
7. **Publicação em dois destinos** a partir da mesma imagem: Hugging Face (Space Docker) e Railway.
8. **Verificação depois do deploy**: confere se o site novo está de pé, na versão certa e sem chave no código da página.

### 1.3 O que NÃO entra agora
- Login de pessoas usuárias e conversas salvas (a conversa vive só na aba do navegador, como hoje).
- Enviar documentos pela interface (continuam entrando pelo repositório).
- Domínio próprio (fica o endereço do Hugging Face e/ou `noa-engenharia-de-dados.up.railway.app`).
- OCR para PDF escaneado.
- Pagamento, planos ou painel administrativo.

---

## 2. Arquitetura: o que roda onde

```
 Navegador (público)              Servidor: 1 contêiner Docker                 Supabase
┌──────────────────────┐  HTTPS  ┌─────────────────────────────────────┐    ┌───────────────────┐
│ Interface React      │ ──────► │  /        → interface compilada     │    │ trechos (producao)│
│ (arquivos estáticos) │         │  /api/... → FastAPI                 │ ─► │ buscar_hibrido()  │
│ só conhece /api      │ ◄────── │    · busca no Supabase (publicável) │    └───────────────────┘
│ NENHUMA chave        │  SSE    │    · monta o prompt (Parte 2)       │    ┌───────────────────┐
└──────────────────────┘         │    · chama a IA com troca automática│ ─► │ OpenRouter (:free │
                                 │  chaves só nas variáveis do serviço │    │ / openrouter/free)│
                                 └─────────────────────────────────────┘    └───────────────────┘
          A MESMA imagem Docker roda no Hugging Face (Space Docker) e no Railway

 GitHub Actions (o portão continua decidindo)
   push na main ─► testes (Python + interface + imagem) ─► avaliar (índice + hit rate) ─► promover (teste → producao)
```

| Lugar | O que roda | O que guarda |
|---|---|---|
| **Navegador** | Interface React compilada (HTML, CSS, JS) | Só a conversa da aba aberta e a preferência de tema. **Nenhuma chave, prompt de sistema ou nome de modelo.** |
| **Servidor** (HF Docker e/ou Railway) | Contêiner com FastAPI (`uvicorn`), o modelo de embedding e a interface compilada | Chaves de IA e chave **publicável** do Supabase, nas variáveis do serviço |
| **Supabase** | Tabela `trechos` e função `buscar_hibrido` (Parte 2, sem mudanças) | Os trechos das coleções `teste` e `producao` |
| **GitHub Actions** | Testes, build da interface, build da imagem, indexação, avaliação e promoção | Chave **secreta** do Supabase (só aqui, como hoje) |

O fluxo de uma pergunta é o mesmo da Parte 2. Muda só a "porta de entrada": em vez do Gradio, a rota `POST /api/perguntar`, que devolve os eventos em SSE. A lógica reaproveita `agente/consulta.py` (`conversar_com_base`, `buscar_producao`), `agente/roteador.py` (`responder`) e `agente/rag.py`.

---

## 3. Stack e restrições conhecidas

| Peça | Escolha | Observação |
|---|---|---|
| Interface | **React 18 + TypeScript**, montada com **Vite**, estilos com **Tailwind CSS** | Poucas dependências. Markdown das respostas com `react-markdown` + `remark-gfm` (tabelas), sem executar HTML vindo do texto. |
| Testes da interface | **Vitest** + Testing Library | Rodam sem navegador real e sem servidor (a API é simulada). |
| Servidor | **FastAPI** + **uvicorn**, Python **3.12** | Mesma versão das Partes 1 e 2. |
| Streaming | **SSE** pela `StreamingResponse` do FastAPI | Sem biblioteca extra. |
| Lógica de IA, RAG e banco | Os módulos atuais: `agente/provedores.py`, `roteador.py`, `consulta.py`, `rag.py`, `config.py`, `erros.py`, `segredos.py` | Reaproveitados. O roteador passa a devolver **eventos** (fontes, texto, fim, erro) em vez de texto com as fontes coladas no fim. |
| Conversão de PDF | **pymupdf4llm** | Licença **AGPL**: roda **só na indexação** (GitHub Actions) e **não vai para a imagem** do servidor. |
| Imagem | **Dockerfile em dois estágios**: `node:24-slim` compila a interface; `python:3.12-slim` recebe o resultado | O modelo de embedding (MiniLM, ~400 MB) é **baixado no build** e fica dentro da imagem. |
| Hospedagem | **Hugging Face (Space Docker)** e **Railway** | Um serviço só por destino: interface e API no mesmo endereço, sem CORS. |

**Restrições que a spec respeita:**
- **Porta:** o servidor escuta em `0.0.0.0:$PORT` (o Railway e o HF Docker informam a porta na variável `PORT`; padrão 7860 no HF, variável no Railway).
- **Memória:** o MiniLM ocupa ~400 MB, que cabe no hardware gratuito do Hugging Face e no Railway.
- **Variáveis:** as chaves ficam nas variáveis do serviço. Mudar uma variável gera um novo deploy.
- **Health check:** a plataforma chama `/api/saude` depois de subir a versão nova. Se não vier 200, a versão antiga continua no ar.
- **Hugging Face Docker:** o `README.md` passa a ter `sdk: docker` e `app_port: 7860` no cabeçalho, em vez de `sdk: gradio`.

---

## 4. Arquivos novos, alterados e removidos

```
agente-personalizado/
├── frontend/                           🆕 a interface
│   ├── package.json / package-lock.json    dependências travadas (npm ci)
│   ├── vite.config.ts                  em desenvolvimento, /api vai para a porta 8000
│   ├── tailwind.config.ts, index.html, tsconfig.json
│   └── src/
│       ├── main.tsx, App.tsx
│       ├── api.ts                      fala com /api (config e perguntar em SSE)
│       ├── tipos.ts                    tipos do contrato da API (seção 5)
│       ├── components/                 Cabecalho, Sugestoes, Conversa, Mensagem, CartaoFonte,
│       │                               CaixaPergunta, AlternarTema, Aviso
│       └── __tests__/                  testes Vitest dos componentes
├── agente/
│   ├── servidor.py                     🆕 FastAPI: rotas /api e entrega da interface
│   ├── limites.py                      🆕 limite de tamanho e de perguntas por minuto/dia (por IP)
│   ├── pdf.py                          🆕 PDF → Markdown (só na indexação)
│   ├── roteador.py                     ✏ devolve eventos (fontes, texto, fim, erro)
│   ├── consulta.py                     ✏ conversar_com_base passa a emitir eventos
│   ├── rag.py                          ✏ carregar_trechos aceita .pdf
│   ├── config.py                       ✏ bloco "servidor" (limites de uso)
│   ├── interface.py                    🗑 a tela Gradio sai
│   └── (provedores, erros, segredos continuam)
├── documentos/
│   └── parte3-frontend-producao.pdf    🆕 a apostila da Parte 3 (hoje é .md; vira .pdf de teste)
├── perguntas_teste.yml                 ✏ + perguntas sobre o PDF
├── Dockerfile, .dockerignore           🆕 imagem em dois estágios
├── railway.json                        🆕 o serviço do Railway como código
├── requirements.txt                    ✏ servidor: saem gradio e spaces, entram fastapi e uvicorn
├── requirements-indexacao.txt          ✏ indexação: fastembed + pymupdf4llm (não vai para a imagem)
├── requirements-dev.txt                ✏ testes (+ httpx para testar a API)
├── app.py                              🗑 sai (o ponto de entrada passa a ser agente/servidor.py)
├── scripts/
│   ├── publicar.py                     ✏ passa a publicar a imagem no HF Docker (ou sai, se o deploy for só por Git)
│   ├── verificar_producao.py           🆕 confere o site no ar depois do deploy
│   └── indexar.py, avaliar.py ...      ✏ indexar lê PDF; o resto continua
├── tests/                              ✏ ajustes da seção 9.2; novos test_servidor.py, test_pdf.py, test_limites.py
├── .github/workflows/
│   ├── deploy.yml                      ✏ testes → interface → imagem → avaliar → promover
│   └── verificar.yml                   🆕 roda depois de cada deploy
├── README.md                           ✏ cabeçalho do HF passa a sdk: docker; entra "como rodar e publicar"
└── SPEC-parte3-…md, ACEITE-parte3.md   📄 documentação
```

**O que sai e por quê:** o Gradio, o `spaces` (ZeroGPU), o `app.py` e a `interface.py` existiam para o Space Gradio. A lógica que importa (provedores, troca automática, RAG, proteção das chaves) **continua** e passa a ser chamada pelo servidor FastAPI.

---

## 5. Contrato da API

Todas as rotas ficam em `/api`. A interface chama **só** caminhos relativos (`/api/...`) e nunca um provedor de IA diretamente.

### 5.1 `GET /api/saude`: o servidor está pronto?
Usada pelo health check da plataforma e pela verificação depois do deploy.

| Situação | Status | Corpo |
|---|---|---|
| Pronto | **200** | `{"status": "ok", "versao": "a1b2c3d", "trechos_na_producao": 614}` |
| Base ligada, mas sem `SUPABASE_URL`/`SUPABASE_PUBLISHABLE_KEY`, banco fora do ar ou modelo que não carregou | **503** | `{"status": "indisponivel", "versao": "a1b2c3d", "motivo": "faltam as variáveis SUPABASE_URL..."}` |

- `versao` = 7 primeiros caracteres de `RAILWAY_GIT_COMMIT_SHA` ou `SPACE_COMMIT` (`"local"` no computador).
- A contagem de trechos é guardada por 60 s, para o health check não consultar o banco a cada chamada.
- O motivo **nunca** contém chave (passa pela limpeza da Parte 1).

### 5.2 `GET /api/config`: o que a interface precisa saber
**200**, só o que é público:
```json
{
  "nome": "NOA Engenharia de Dados",
  "descricao": "Engenharia de Dados, estatística e machine learning, passo a passo.",
  "exemplos": ["Como funciona a busca híbrida com RRF?", "..."],
  "logo_url": "/api/logo",
  "cores": {"principal": "#123330", "secundaria": "#0F2B28", "destaque": "#EC8098"},
  "limites": {"max_caracteres_pergunta": 2000},
  "mensagem_nao_encontrado": "Não encontrei isso no material do curso."
}
```
**Nunca** contém: `instrucoes` (o prompt de sistema), nomes de provedores ou de modelos, temperatura, chaves, endereço do Supabase.

### 5.3 `GET /api/logo`: a logo do `config.yaml`
**200** com o arquivo (`image/png` ou `image/svg+xml`), com cache de 1 hora. **404** se o arquivo sumir.

### 5.4 `POST /api/perguntar`: a pergunta, respondida em streaming
**Recebe** (JSON): `{"mensagem": "...", "historico": [{"papel": "usuario", "texto": "..."}, {"papel": "assistente", "texto": "..."}]}`
- `mensagem`: texto, obrigatório, sem ser só espaços.
- `historico`: opcional, até 20 mensagens, cada uma com `papel` (`usuario`/`assistente`) e `texto` de até 8.000 caracteres. O servidor usa só as últimas `ia.max_mensagens_historico` (Parte 1).
- **Qualquer outro campo é recusado** (422). Não dá para pedir outro modelo, temperatura ou prompt.

**Devolve** (`200`, `text/event-stream`), nesta ordem:

| Evento | Quando | Dados |
|---|---|---|
| `fontes` | Logo depois da busca, antes do texto. Só quando há trechos | `[{"n": 1, "fonte": "parte2-rag.md", "secao": "12 Recuperação híbrida e RRF", "trecho": "..."}]` |
| `texto` | Várias vezes, a cada pedaço gerado | `{"delta": "O RRF "}` |
| `fim` | Uma vez, no final | `{"nao_encontrado": false}` (true quando a resposta é a frase de "não encontrei"; aí a interface não mostra cartões) |
| `erro` | No lugar do `fim`, se não deu para responder | `{"tipo": "provedores", "mensagem": "😕 Não consegui responder agora. Motivos: ..."}` |

- Tipos de `erro`: `provedores` (todos falharam, inclui 429/404/403 do OpenRouter), `interrompida`, `sem_chave`, `base_indisponivel`.

**Erros antes do streaming** (JSON comum): **413** (pergunta acima de `max_caracteres_pergunta`), **422** (JSON inválido, mensagem vazia, campo desconhecido, histórico grande), **429** (passou de 10/min ou 100/dia neste IP, com `Retry-After`), **503** (servidor ainda carregando o modelo). Ordem: validação (422) → tamanho (413) → limite (429).

### 5.5 `/` e demais caminhos: a interface
O servidor entrega `frontend/dist`. Caminhos desconhecidos fora de `/api` devolvem o `index.html`; os de `/api` desconhecidos devolvem 404 em JSON.

---

## 6. Requisitos funcionais (continuação a partir de RF41)

**Interface (RF41 a RF55):** streaming visível; cartões de fonte clicáveis que abrem o trecho; sugestões na tela inicial vindas de `/api/config`; modo claro/escuro salvo no navegador; responsivo no celular (360 px) sem rolagem lateral; estados vazio, pensando, erro com "Tentar de novo" e "não encontrei"; Markdown seguro nas respostas; contador de caracteres perto do limite; tudo em português; nenhuma chave no JS.

**Servidor (RF56 a RF66):** as 4 rotas da seção 5; limites por IP (413/429) conferidos no servidor; `/api/config` sem segredos; o roteador emite eventos; health check com cache de 60 s; cabeçalhos de segurança (`X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Content-Security-Policy`); logs sem texto de pergunta, sem chave e com IP mascarado; troca automática de provedor preservada (Parte 1); frase exata de "não encontrei" preservada (Parte 2); a interface compilada servida pelo mesmo endereço.

---

## 7. Como os PDFs entram na base de conhecimento

**Onde:** na indexação (`scripts/indexar.py`, no GitHub Actions). O servidor **não** lê PDF; ele só busca no Supabase.

**Passo a passo (`agente/pdf.py`, com pymupdf4llm):**
1. Extrair o texto página por página, já em Markdown (títulos pelo tamanho da fonte, tabelas convertidas).
2. Detectar PDF escaneado: se o documento tiver menos de 200 caracteres de texto, a indexação **para** com mensagem clara ("PDF escaneado, sem texto; OCR fica fora deste projeto").
3. Remover cabeçalho e rodapé: linhas repetidas em mais da metade das páginas.
4. Remover números de página soltos.
5. Arrumar títulos: tirar negrito, juntar espaços, manter níveis 1 a 3.
6. Garantir o título do documento (metadados ou nome do arquivo).
7. Dividir em trechos como os `.md` da Parte 2, usando `agente/rag.py`. A `fonte` do trecho é o nome do PDF.

**Validação da pasta (amplia a regra atual de `carregar_trechos`):** aceita `.md` e `.pdf`; cada PDF até 20 MB, sem senha, com texto extraível; o nome segue a regra atual (minúsculas, números e hífens).

**Perguntas de teste:** o `perguntas_teste.yml` ganha perguntas sobre o PDF (metade com palavras do texto, metade com outras), apontando `fonte_esperada` para o nome do PDF. Conversão ruim derruba o hit rate e o portão barra a publicação.

---

## 8. Segurança: chaves, limites e o que nunca vai para o navegador

| Segredo / dado | Onde fica | Quem usa | Nunca em |
|---|---|---|---|
| `OPENROUTER_API_KEY` (e opcionais `ANTHROPIC`/`OPENAI`) | Variáveis do serviço (HF/Railway) | servidor | navegador, repositório, `railway.json`, imagem, logs |
| `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` | Variáveis do serviço | servidor (só lê a produção) | navegador |
| `SUPABASE_URL`, `SUPABASE_SECRET_KEY` | Secrets do GitHub | jobs `avaliar` e `promover` | serviço, navegador, imagem |
| Prompt de sistema, provedores e modelos | `config.yaml`, lido pelo servidor | servidor | `/api/config`, navegador |

**Regras:** nada de `VITE_` com segredo; a API só aceita `mensagem` e `historico`; todo limite vale no servidor; a imagem não recebe chave (nem `ARG` nem `ENV`); Markdown sem executar HTML; cabeçalhos de segurança em todas as respostas; logs sem pergunta/chave e com IP mascarado; injeção de prompt por documento tratada como na Parte 2.

---

## 9. Verificações do portão

### 9.1 Novas

| # | Onde roda | Verificação |
|---|---|---|
| **T18** | job `testes` (sem rede) | **Contrato da API** com o cliente de testes do FastAPI e busca/IA simuladas: ordem dos eventos de `/api/perguntar`, casos 413/422/429/503, `/api/saude` 200/503 |
| **T19** | job `testes` | **Nada de segredo exposto:** `/api/config` sem `instrucoes`/provedores/modelos/chaves; a interface não usa `import.meta.env`/`VITE_`; `railway.json` e `Dockerfile` sem chave |
| **T20** | job `interface` (Node) | `npm ci`, `tsc --noEmit`, testes Vitest e `npm run build`. A varredura de chaves roda também sobre `frontend/dist` |
| **T21** | job `testes` | **PDF:** a conversão remove cabeçalho/rodapé/número de página, arruma títulos, e um PDF escaneado dá mensagem clara |
| **T22** | job `imagem` | **Docker:** a imagem é montada (sem chaves) e sobe; `/api/saude` responde (503 sem Supabase, esperado), `/` entrega a interface |
| **T23** | job `testes` | **`railway.json`:** builder `DOCKERFILE`, `healthcheckPath: /api/saude`, timeout ≥ 120 s, reinício `ON_FAILURE`, sem segredo |
| **T24** | job `verificar` (após deploy) | O site no ar responde `/api/saude` com 200 e a versão do commit, `/api/config` sem segredo, nenhuma chave no HTML/JS |

> Os números T18+ continuam a numeração atual deste repositório (hoje vai até T17). Os testes do Gradio/`app.py` são substituídos por equivalentes do FastAPI; os testes de RAG, config, provedores, roteador e segredos continuam.

### 9.2 O que muda nos testes das Partes 1 e 2
As garantias continuam. Mudam só os testes ligados ao Gradio e ao Hugging Face Gradio:
- `test_app.py` (app Gradio sobe sem chave) → passa a testar o servidor FastAPI subindo sem chave e `/api/perguntar` com `erro: sem_chave`.
- `test_readme.py` (cabeçalho Gradio) → passa a conferir o cabeçalho `sdk: docker` e o `requirements.txt` do servidor sem bibliotecas de indexação.
- Testes de `publicar.py` ligados ao Space Gradio → ajustados ao novo destino (HF Docker/Railway).
- `test_consulta.py`, `test_roteador.py`: ajustados para a saída em eventos (fontes/texto/fim) em vez de texto com fontes coladas.
- Demais testes (config, provedores, segredos, trechos, indexação, avaliação, diagnóstico, gratuito): sem mudança.

---

## 10. Pipeline de deploy

```
push na main
   ├─► job "testes"     (Python, sem rede)
   ├─► job "interface"  (Node: tipos, testes, build, chaves no dist)
   └─► job "imagem"     (docker build + sobe o contêiner + chamadas)
            │ todos verdes?   não ─► ❌ para. Nada publica.
            ▼
       job "avaliar"     indexa a coleção "teste" (.md e .pdf) + hit rate
            │ passou?        não ─► ❌ para. "producao" e site intactos.
            ▼
       job "promover"    "teste" vira "producao" (uma transação)
            │
            ▼
       deploy (HF Docker e/ou Railway) ─► health check /api/saude
            │ 200? não ─► versão antiga continua no ar
            ▼
       job "verificar"   confere o site no ar (versão, sem chave)
```

**`railway.json`** (no repositório, sem segredos):
```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": { "builder": "DOCKERFILE", "dockerfilePath": "Dockerfile" },
  "deploy": { "healthcheckPath": "/api/saude", "healthcheckTimeout": 300, "restartPolicyType": "ON_FAILURE", "restartPolicyMaxRetries": 3 }
}
```

**Dockerfile em dois estágios:** estágio `node:24-slim` roda `npm ci && npm run build` e gera `frontend/dist`; estágio `python:3.12-slim` instala o `requirements.txt` (sem pymupdf4llm), baixa o modelo de embedding, copia `agente/`, `config.yaml`, `assets/` e o `dist`, roda como usuário sem privilégios e inicia com `uvicorn agente.servidor:app --host 0.0.0.0 --port ${PORT:-7860}`.

**Configuração feita uma vez, fora do repositório:**

| Passo | Quem | Onde |
|---|---|---|
| Converter o Space de Gradio para **Docker** (ou criar um Space Docker novo) | Você (eu guio) | Hugging Face → Space → Settings |
| Criar o projeto `noa-engenharia-de-dados` no Railway, ligado ao repo | Você (eu guio), opcional | Railway |
| Cadastrar as variáveis (chave de IA, `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`) | **Você** (as chaves não passam por mim) | HF Space → Variables/Secrets e/ou Railway → Variables |
| Ligar **Wait for CI** (se usar Railway) | Você (eu guio) | Railway → Settings → Source |
| Criar a variável `URL_PRODUCAO` | Você | GitHub → Settings → Variables |

---

## 11. Critérios de aceite

- [ ] Abro o endereço e vejo a interface com a minha logo e as minhas cores, no computador e no celular (360 px), sem rolagem lateral.
- [ ] Alterno entre modo claro e escuro. A escolha fica salva ao recarregar.
- [ ] A tela inicial mostra as sugestões. Clico numa e a resposta chega aos poucos.
- [ ] A resposta sobre o material tem cartões de fonte. Ao clicar, vejo o trecho usado.
- [ ] Pergunta fora do material: aparece "Não encontrei isso no material do curso.", sem cartões.
- [ ] "Oi, tudo bem?" recebe resposta normal, sem cartões.
- [ ] Coloco um PDF com texto em `documentos/` com uma pergunta de teste sobre ele, faço commit, e o assistente passa a responder sobre o PDF, com o cartão mostrando o nome do PDF.
- [ ] Coloco um PDF escaneado: o portão para com a mensagem de PDF sem texto, e o site continua como estava.
- [ ] Abro o código-fonte da página e os arquivos JS e não encontro chave, prompt nem nome de modelo.
- [ ] Mando perguntas seguidas: na 11ª dentro de um minuto, aparece "Muitas perguntas seguidas. Tente de novo em N segundos".
- [ ] Descomento as perguntas impossíveis: o `avaliar` fica vermelho, o deploy não acontece e o site no ar continua funcionando.
- [ ] Depois de um deploy, a verificação fica verde e mostra a versão do commit.
- [ ] Desligo o servidor e a interface mostra o erro com "Tentar de novo", sem perder a pergunta.
- [ ] A mesma imagem Docker roda no Hugging Face e no Railway.
- [ ] Todos os testes das Partes 1 e 2 continuam passando, com os ajustes da seção 9.2.

---

## 12. Ordem das tarefas (uma de cada vez)

| # | Tarefa | Entrega | Como testar |
|---|---|---|---|
| **1** | **Servidor FastAPI** | `agente/servidor.py`, `agente/limites.py`; roteador em eventos; bloco `servidor` no config; T18, T19, ajuste de T15/T16 | Rodar o servidor no computador e chamar as rotas (eu passo os comandos `curl`) |
| **2** | **PDF na base** | `agente/pdf.py`, `rag.py` aceitando `.pdf`, T21, a apostila em `documentos/`, perguntas novas, `requirements-indexacao.txt` | Ver os trechos do PDF; relatório do avaliar com o PDF |
| **3** | **Interface: estrutura e estados** | Projeto Vite/React/TS/Tailwind; componentes; todos os estados com a API simulada; T20 | `npm run dev` e ver cada estado |
| **4** | **Interface: visual e acabamento** | Cores e logo do config, tema escuro, celular, Markdown, cartões de fonte; ligada à API de verdade | Conversar de ponta a ponta com o banco real |
| **5** | **Imagem Docker e `railway.json`** | `Dockerfile`, `.dockerignore`, `railway.json`; T22 e T23 | O job `imagem` verde; comandos para rodar a imagem no computador |
| **6** | **Pipeline** | Jobs `interface`, `imagem` e `promover`; `verificar.yml` com T24; sai o Gradio (`app.py`, `interface.py`); README com `sdk: docker` | Botão manual numa branch: tudo verde, sem promover |
| **7** | **No ar** | Space convertido para Docker (e, opcional, Railway); você cadastra as variáveis; levamos para a `main` | Abrir o endereço; verificação verde |
| **8** | **Aceite** | `ACEITE-parte3.md` com os roteiros da seção 11 | Marcar cada item |

> Entre as tarefas 1 e 6, nada vai para a `main`: o Space continua no ar com a Parte 2 até a Parte 3 estar pronta e aprovada.

---

## 13. Erros comuns e como resolver

| Sintoma | Causa provável | Conserto |
|---|---|---|
| Página em branco no deploy | `frontend/dist` ausente na imagem, ou base errada no Vite | Conferir o estágio de build e `base: "/"` no Vite |
| `/api/saude` responde 503 | Faltam `SUPABASE_URL`/`SUPABASE_PUBLISHABLE_KEY`, ou banco fora do ar | Conferir as variáveis do serviço |
| Erro de rede no chat (local) | API local fora do ar ou proxy do Vite errado | Subir o `uvicorn` na porta 8000 |
| Chave no JavaScript publicado | Variável `VITE_` com segredo | Remover, revogar a chave, manter só no servidor |
| PDF sem texto extraível | PDF escaneado | Usar um PDF com texto; OCR fica fora |
| Muitos 429 numa sala de aula | Todos atrás do mesmo IP | Aumentar o limite de perguntas por minuto |
| Chat responde 429/404/403 do OpenRouter | Modelo gratuito bloqueado/lotado | Troca automática de provedor e `openrouter/free`; ver a seção de modelos reserva |

---

> **Nota desta adaptação:** esta spec segue as mesmas decisões da aula (Parte 3), adaptadas à estrutura real deste repositório: módulos `consulta.py`/`roteador.py`/`rag.py` em vez de `banco.py`/`embeddings.py`/`documentos.py`; modelo de embedding MiniLM (384) em vez do e5-base (768); publicação por Docker no Hugging Face gratuito além do Railway. "Os nomes mudam; as decisões são equivalentes."
