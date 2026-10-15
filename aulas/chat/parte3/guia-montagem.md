# Guia de montagem: Parte 3, Front-end e Produção

Material do Instituto NTA, fornecido no curso. Fonte: Guia_Montagem_Parte3.pdf.
Conversão textual para consulta. Tabelas e exemplos podem ter diagramação diferente do PDF original.

INSTITUTO NTA
Instituto Nacional de Tecnologia Aplicada
## Construindo seu Chat
## de IA Personalizado
## Guia de montagem · Parte 3
Do Gradio no Hugging Face a um produto no ar:
interface React, PDF na base e deploy no Railway
Parte 3 de 3  ·  08/10  ·  Guia de montagem
Prof. Thiago Azeredo Rodrigues
Complementa a apostila da Parte 3 (Front-end com IA e Produção)
Continua os guias de montagem das Partes 1 e 2

INSTITUTO NTA
Guia de montagem  ·  Parte 3
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
2
## 00  Como usar este guia
A apostila da Parte 3 explica os conceitos: front-end e back-end, API, streaming, React, Docker,
PaaS. Este guia conta a montagem: como o projeto da Parte 2 virou um produto com interface
própria, PDF na base e deploy de produção, na ordem em que foi feito, com o que testamos em
cada passo e os problemas reais que apareceram, inclusive uma troca de plataforma no meio do
caminho.
O ponto de partida é o projeto da Parte 2 funcionando: repositório no GitHub, o portão com os
três jobs e a base de conhecimento no Supabase.
O resultado final
Você
muda o config.yml,
o front-end ou
um PDF em
documentos/ e
faz commit
GitHub Actions
testar: T1 a T17
+ build do front
avaliar: índice + T14
publicar: promove
o índice
Railway
Wait for CI: espera
os 3 jobs passarem
monta a imagem
(Dockerfile) e troca
a versão se /api/saude
push
verde
Supabase
coleções teste
e producao
busca híbrida
Servidor (FastAPI)
/api/perguntar:
busca, prompt e
resposta em SSE
Qualquer pessoa
abre a interface
React e recebe a
resposta com fontes
trechos
streaming
roda
O que você precisa antes de começar
Item
Para quê
O projeto da Parte 2 no ar
É a base: a busca, o banco e o portão continuam os mesmos
Conta no Railway (entrando com o
GitHub)
Hospedar o serviço com Docker, HTTPS e health check
Um PDF com texto da sua área
Testar a nova leitura de PDF. PDF escaneado (só imagem) não
serve
Chave do OpenRouter (ou outro
provedor)
A mesma das partes anteriores; agora vai para o Railway
Assistente de programação
Gerar a spec e o código: Claude Code, Codex, Cursor ou
Antigravity

INSTITUTO NTA
Guia de montagem  ·  Parte 3
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
3
Arquivos que entram, mudam e saem
frontend/                    NOVO   interface React + Vite + Tailwind (src/, package.json)
servidor.py                  NOVO   FastAPI: /api/saude, /api/config, /api/perguntar e o front-end
chat.py                      NOVO   provedores de IA e geração da resposta (veio do app.py)
testes_api.py                NOVO   testes da API com busca e provedor simulados (T16)
Dockerfile, .dockerignore    NOVOS  a imagem do serviço, em dois estágios
railway.json                 NOVO   build pelo Dockerfile e health check em /api/saude
documentos/*.pdf             NOVO   PDFs agora entram (o .gitignore libera só esta pasta)
rag.py                       MUDA   lê .md e .pdf
testes.py                    MUDA   T6 e T11 ajustados; + T15 e T17
config.yml                   MUDA   + bloco interface (opcional)
requirements.txt             MUDA   + fastapi, uvicorn; - gradio
.github/workflows/deploy.yml MUDA   build do front no testar; publicar só promove o índice
app.py                       SAI    o Gradio deu lugar ao React + FastAPI
## 01  Da ideia à spec
Como nas partes anteriores, nada de código antes da spec. O IDEIA-parte3.md descreve em
linguagem simples o que queremos: interface bonita, PDF na base, endereço próprio e o portão
continuando a decidir o que vai para o ar. No fim dele está o prompt que pede ao assistente a
SPEC-parte3-frontend-producao.md.
As perguntas que o assistente fez
Pergunta
O que respondemos
Por quê
Como gerar o
front-end?
React + Vite pelo assistente
Código nosso, versionado e testável;
dá para pedir ajustes visuais à IA
Onde hospedar?
Tudo num serviço só: a API e a
interface
Um endereço, sem CORS e sem duas
plataformas para cuidar
Qual endereço?
O subdomínio da plataforma
Domínio próprio fica como passo
opcional (seção 11)
Limites de uso?
2.000 caracteres e 10 perguntas por
minuto
Protege a chave de IA; ajustável no
config.yml
A spec foi revisada e aprovada antes da primeira linha de código. Ela foi atualizada duas vezes
durante a montagem: para registrar as versões novas das bibliotecas (React 19, Tailwind 4) e a
troca do Render pelo Railway (seção 07). Spec não é contrato fechado: é o registro do que foi
decidido, e muda quando a realidade muda.
## 02  O servidor: FastAPI no lugar do Gradio
O primeiro passo foi separar o "cérebro" do chat da interface. O que o app.py fazia (escolher o
provedor, buscar os trechos, montar o prompt, chamar o modelo) foi para o chat.py, sem mudar
o comportamento. O servidor.py expõe isso como uma API:

INSTITUTO NTA
Guia de montagem  ·  Parte 3
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
4
Rota
O que faz
GET /api/saude
Diz se o servidor está pronto, a versão (commit) e quantos trechos há na
produção. Responde 503 se o Supabase não estiver configurado
GET /api/config
Nome, descrição, cores, logo, exemplos e limites. Nunca chaves, modelos ou
prompt
POST /api/perguntar
Recebe a pergunta e o histórico; devolve a resposta aos poucos (eventos
fontes, texto, fim ou erro)
/ (o resto)
Os arquivos do front-end compilado (frontend/dist)
Como testamos
•
Automático: o testes_api.py simula a busca e o provedor de IA e confere a ordem dos
eventos, os erros 413 (pergunta longa), 422 (vazia) e 429 (muitas por minuto), a mensagem
amigável sem chave e que o /api/config não vaza segredo. Resultado: 9 testes passando.
•
Manual: subimos o servidor localmente com uvicorn servidor:app --port 8000 e
chamamos cada rota.
Por que os limites ficam no servidor
Desabilitar o botão na interface não protege nada: quem quiser abusar chama a API direto. O
tamanho máximo e as perguntas por minuto são conferidos no servidor, por IP do visitante.
## 03  O front-end: React + Vite + Tailwind
Com a API pronta, o assistente gerou a interface em frontend/. Ela só conhece as rotas /api:
nenhuma chave, nenhum prompt. Os componentes:
Componente
O que mostra
Cabecalho
Logo, nome, descrição, "Nova conversa" e o botão de tema claro/escuro
Sugestoes
A tela inicial: logo grande, nome em degradê e os exemplos do config.yml
como cartões
Conversa e Mensagem
As mensagens, o "Consultando o material…", a resposta em Markdown
chegando aos poucos, o botão copiar e os avisos de erro com "Tentar de novo"
CartaoFonte
Cada fonte numerada; ao clicar, abre o trecho usado. PDFs ganham uma
etiqueta
CaixaPergunta
Caixa que cresce com o texto; Enter envia, Shift+Enter quebra a linha;
contador perto do limite
Rodar no computador
uvicorn servidor:app --reload --port 8000      # terminal 1: a API
cd frontend && npm install && npm run dev      # terminal 2: http://localhost:5173
O Vite repassa as chamadas /api para a porta 8000 (proxy no vite.config.js). Conferimos no
computador e numa tela de celular (360 px), nos temas claro e escuro, sem rolagem lateral.

INSTITUTO NTA
Guia de montagem  ·  Parte 3
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
5
## 04  PDF na base de conhecimento
Na Parte 2, o PDF ficava fora por causa do Hugging Face, que recusava binários. Fora dele, o PDF
pode entrar, e quem cuida da conversão é o próprio pipeline:
•
O rag.py converte cada PDF para Markdown com o pymupdf4llm, página por página.
•
Linhas curtas que se repetem em mais da metade das páginas (cabeçalho e rodapé) e
números de página soltos são removidos.
•
Títulos longos que o PDF quebrou em duas linhas são juntados de novo, para a seção do
trecho ficar certa.
•
Se sobrar menos de 200 caracteres, a indexação para com PDF sem texto extraível
(escaneado?).
•
No .gitignore, a regra !documentos/*.pdf libera só os PDFs da base.
Como PDF de exemplo usamos a própria apostila da Parte 3. Ela virou 42 trechos, e entrou uma
pergunta de teste sobre ela no perguntas_teste.yml.
- pergunta: Para que serve a opção Wait for CI do Railway?
fonte_esperada: parte3-frontend-producao.pdf
secao_esperada: Railway
No portão: hit rate 8/9 = 0,89 (limiar 0,85), com o trecho do PDF em 2º lugar. A indexação só
precisa do pymupdf4llm no GitHub Actions; o servidor no ar não usa essa biblioteca.
## 05  O portão da Parte 3
Teste
O que confere
T6 (ajustado)
A sintaxe do servidor.py e do chat.py (o app.py saiu)
T11 (ajustado)
A pasta de documentos aceita .md e .pdf; Word e outros formatos barram
T15
O bloco interface do config.yml: tema_inicial, rodape, limite_caracteres,
perguntas_por_minuto
T16
A API: os 9 testes do testes_api.py
T17
O front-end compilado não tem chave nem nome de variável secreta; nenhum
frontend/.env no Git
Cada teste novo foi conferido também "pelo avesso": colocamos um valor errado no config.yml,
um .docx na pasta, um nome de chave no build e um .env versionado, e o portão barrou cada
caso com uma mensagem clara.
O job testar agora instala o Node e roda npm ci && npm run build antes dos testes. E o
workflow passou a rodar também em pull requests: o portão responde antes do merge, sem
publicar nada.
## 06  O contêiner: Dockerfile em dois estágios

INSTITUTO NTA
Guia de montagem  ·  Parte 3
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
6
FROM node:20-slim AS frontend          # estágio 1: compila o front-end
RUN npm ci && npm run build
FROM python:3.11-slim                  # estágio 2: o servidor
COPY --from=frontend /frontend/dist ./frontend/dist
RUN pip install -r requirements.txt
RUN python -c "...TextEmbedding(..., lazy_load=True)"   # baixa o modelo no build
COPY . .
USER assistente                        # não roda como root
CMD uvicorn servidor:app --host 0.0.0.0 --port ${PORT:-8000}
•
O modelo de embedding é baixado no build: o serviço sobe sem depender do Hugging Face.
•
Só a pasta dist do estágio 1 vai para a imagem final; o Node fica para trás.
•
Testamos localmente: a imagem subiu, serviu a página e respondeu 503 no /api/saude sem as
variáveis do Supabase, que é exatamente o que impede uma versão quebrada de entrar no
ar.
## 07  A primeira tentativa: Render, e por que
## saímos
A spec original previa o Render. O serviço foi criado (Web Service, Docker, região Virginia, plano
de 512 MB) e o primeiro build parou assim:
#12 [stage-1 4/9] RUN pip install -r requirements.txt
...
==> Out of memory (used over 512Mi)
Tentativa
O que mudamos
Resultado
1
Nada: o primeiro build
Estourou: o npm e o pip rodavam
ao mesmo tempo
2
Estágios um de cada vez e o modelo só baixado
(lazy_load)
Estourou de novo, no pip install, já
sozinho
Diagnóstico
O Render limita o build à mesma memória do
plano
Ajuste no Dockerfile não resolve
As saídas eram pagar o plano de 2 GB, montar a imagem no GitHub Actions ou trocar de
plataforma. Escolhemos o Railway: o build roda em máquinas separadas, o painel é parecido e o
preço é por uso. Como o projeto já tinha Dockerfile, a troca custou poucos arquivos:
•
Saiu o render.yaml, entrou o railway.json (builder Dockerfile e health check).
•
O /api/saude passou a ler a versão de RAILWAY_GIT_COMMIT_SHA.
•
O pipeline ficou mais simples: sem Deploy Hook e sem job verificar. Quem liga o Railway ao
portão é a opção Wait for CI, e quem confere o site é o health check.
A lição para levar
Plataformas parecidas diferem nos limites que não aparecem na primeira página: memória
do build, se o serviço dorme, como cobram. E o que tornou a troca barata foi o contêiner:
com Dockerfile, a aplicação não pertence à plataforma.

INSTITUTO NTA
Guia de montagem  ·  Parte 3
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
7
## 08  Railway: criar e configurar o serviço
1. Em railway.com, entre com o GitHub. New Project → Deploy from GitHub repo e escolha o
repositório.
2. Variables: cadastre OPENROUTER_API_KEY (e, se usar, ANTHROPIC_API_KEY e
OPENAI_API_KEY), SUPABASE_URL e SUPABASE_PUBLISHABLE_KEY. A SUPABASE_SECRET_KEY
nunca vai para o servidor: ela fica só no GitHub.
3. Settings → Networking → Generate Domain. Sem isso o serviço aparece como
"Unexposed service".
4. Settings → Source: branch main e Wait for CI ligado.
5. O health check (/api/saude, até 300 segundos) já vem do railway.json.
O que vimos no caminho
O que apareceu
O que era
Serviço "python@3.13" rodando a
versão antiga
O Railway publicou a main antes do merge, ainda com o
app.py e sem Dockerfile. Normal: some quando a main
recebe o código novo
"Unexposed service"
Faltava gerar o domínio
Log: Base de conhecimento… variável
de ambiente ausente
As variáveis do Supabase ainda não estavam cadastradas; o
/api/saude respondia 503
Chat: "O assistente ainda não foi
configurado com uma chave de IA"
Faltava a OPENROUTER_API_KEY. Depois de cadastrar, o
Railway republica sozinho
Log: modelo carregado; 178 trechos
na produção
Tudo certo: servidor no ar com a base, incluindo o PDF
## 09  Merge e o primeiro deploy pelo portão
1. O trabalho foi feito numa branch. O portão rodou nela (testar e avaliar) antes de qualquer
merge.
2. Abrimos o pull request e fizemos o merge na main com squash (um commit só, histórico
limpo).
3. Na main, os três jobs rodaram: testar (T1 a T17 e o build), avaliar (índice com o PDF e as
perguntas) e publicar (promove o índice testado para a produção).
4. Com os três verdes, o Railway montou a imagem do commit da main e trocou a versão depois
que o /api/saude respondeu.
Confira o Wait for CI
Sem ele, o Railway publica todo commit da main na hora, mesmo se o portão falhar. Abra
Settings → Source e confira que está ligado. É o mesmo cuidado que na Parte 1 tivemos com
o deploy automático.

INSTITUTO NTA
Guia de montagem  ·  Parte 3
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
8
## 10  Testar no ar
Teste
Esperado
Abrir o endereço no computador e no celular
Logo, nome, cores do config.yml e os exemplos como
cartões
Alternar o tema
Claro e escuro; a escolha fica salva no navegador
Pergunta do material
Resposta aos poucos e cartões de fonte que abrem o
trecho
"Para que serve a opção Wait for CI do
Railway?"
Fonte com a etiqueta PDF: a resposta veio da apostila em
PDF
"Qual a capital da Austrália?"
"Não encontrei isso no material do curso.", sem fontes
Mais de 10 perguntas em um minuto
Aviso amarelo pedindo para esperar (429)
Ver o código-fonte da página (Ctrl+U)
Nenhuma chave em lugar nenhum
Abrir /api/saude
status ok, a versão (commit) e trechos_na_producao
A demonstração do portão
1. Descomente as duas perguntas impossíveis do perguntas_teste.yml e faça commit.
2. O avaliar fica vermelho, o publicar não roda e o Railway não publica: o site continua igual.
3. Comente de novo, faça commit e veja o verde voltar e o Railway publicar.
## 11  Personalizar: a interface é sua
Onde
O que muda
Precisa de código?
config.yml
nome, descricao, tema (cores), logo, exemplos
Não
config.yml → interface
tema_inicial, rodape, limite_caracteres,
perguntas_por_minuto
Não
frontend/src/
layout, componentes, textos da tela, animações
Sim: peça ao assistente
e revise
Railway → Networking
subdomínio .up.railway.app ou domínio próprio
Não
Para mudanças visuais, descreva o resultado, não o código: "deixe os cartões de sugestão com
ícones e um degradê suave", "mostre a data em cada mensagem". Toda mudança passa pelo
portão antes de ir para o ar.
Domínio próprio
1. No Railway: Settings → Networking → Custom Domain, por exemplo chat.seudominio.com.br.
2. No painel do domínio (Registro.br, Cloudflare...), crie o CNAME (e o TXT, se pedir) que o
Railway mostrar.
3. Espere a verificação; o HTTPS sai sozinho. Na Cloudflare, deixe o registro como "DNS only" até
o certificado sair.

INSTITUTO NTA
Guia de montagem  ·  Parte 3
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
9
## 12  Checklist de aceite da Parte 3
Critério
Como conferir
CA20
Front e API rodam juntos no computador
npm run dev + uvicorn
CA21
A imagem Docker sobe e serve a página
Build no Railway ou docker build
CA22
O endereço abre a interface com a sua identidade
Navegador
CA23
Resposta em streaming com cartões de fonte
Chat
CA24
Tema escuro e celular funcionam
Navegador e celular
CA25
Pergunta fora do material: "não encontrei", sem fontes
Chat
CA26
Nenhuma chave na página ou no JavaScript
T17 e Ctrl+U
CA27
Um PDF com texto passa no portão e vira fonte
Log do avaliar e chat
CA28
PDF escaneado barra a indexação com mensagem clara
Log do avaliar
CA29
Perguntas demais: aviso de espera (429)
Chat
CA30
Perguntas impossíveis barram o deploy; o site não muda
Seção 10
CA31
Três jobs verdes e o Railway publica o commit
Actions, Railway e /api/saude
Fechando o curso
Nas três partes, o mesmo método: ideia em linguagem simples, spec revisada,
implementação uma tarefa por vez e um portão automático decidindo o que vai para o ar.
Mudaram a interface, a base de conhecimento e até a plataforma; o método ficou. É ele que
você leva para o próximo projeto.
