# Guia de montagem: Parte 2, RAG

Material do Instituto NTA, fornecido no curso. Fonte: Guia_Montagem_Parte2.pdf.
Conversão textual para consulta. Tabelas e exemplos podem ter diagramação diferente do PDF original.

INSTITUTO NTA
Instituto Nacional de Tecnologia Aplicada
## Construindo seu Chat
## de IA Personalizado
## Guia de montagem · Parte 2
Do chat genérico ao assistente que consulta o material:
documentos, Supabase, busca híbrida e portão de qualidade
Parte 2 de 3  ·  01/10  ·  Guia de montagem
Prof. Thiago Azeredo Rodrigues
Complementa a apostila da Parte 2 (RAG e Base de Conhecimento)
Continua o guia de montagem da Parte 1

INSTITUTO NTA
Guia de montagem  ·  Parte 2
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
2
## 00  Como usar este guia
A apostila da Parte 2 explica os conceitos: embeddings, similaridade, chunking, busca híbrida,
RRF. Este guia conta a montagem: como o projeto da Parte 1 virou um assistente que responde
com base no material do curso, na ordem em que foi feito, com o que testamos em cada passo e
os problemas reais que apareceram até o primeiro deploy verde.
O ponto de partida é o projeto da Parte 1 funcionando: repositório no GitHub, Space no Hugging
Face e o deploy automático pelo GitHub Actions.
O resultado final
Você
coloca .md em
documentos/ e
faz commit
GitHub Actions
testar: T1 a T13
avaliar: indexa na
coleção teste e roda
as perguntas (T14)
publicar: promove
Supabase
tabela trechos
coleções teste
e producao
busca híbrida (SQL)
push
grava
Hugging Face Space
busca os trechos
na producao e
monta o prompt
Provedor de IA
responde só com
base nos trechos
Qualquer pessoa
pergunta e recebe
a resposta com
as fontes
lê
trechos
resposta
O que você precisa antes de começar
Item
Para quê
O projeto da Parte 1 no ar
É a base: o RAG entra antes da chamada ao modelo, sem
reescrever o chat
Conta no Supabase (plano
gratuito)
Guardar os trechos e os vetores, e fazer a busca
De 3 a 5 documentos da sua área
O material de consulta do assistente. Nada de dado pessoal ou
sigiloso
Assistente de programação
Gerar a spec e o código: Claude Code, Codex, Cursor ou Antigravity
Arquivos que entram e que mudam
documentos/                  NOVO   o material de consulta, só .md
supabase/esquema.sql         NOVO   tabela, busca híbrida e permissões do banco
rag.py                       NOVO   ler, dividir em trechos, embeddings, buscar, montar o prompt
indexar.py                   NOVO   grava a coleção 'teste'; com --promover, vira 'producao'
avaliar.py                   NOVO   faz as perguntas de teste na coleção 'teste' (T14)
perguntas_teste.yml          NOVO   perguntas com a fonte esperada e o limiar
IDEIA-parte2.md, SPEC-parte2-rag.md   NOVOS
app.py                       MUDA   busca os trechos antes de chamar o modelo e lista as fontes
config.yml                   MUDA   bloco base_conhecimento e regras de RAG no prompt
testes.py                    MUDA   + T10 a T13
requirements.txt             MUDA   + fastembed, supabase
.github/workflows/deploy.yml MUDA   + job avaliar entre testar e publicar

INSTITUTO NTA
Guia de montagem  ·  Parte 2
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
3
## 01  Preparar o material de consulta
O material de consulta do projeto de referência são as próprias apostilas das Partes 1 e 2. Como
estavam em PDF, o primeiro passo foi convertê-las para Markdown.
1. Converter: usamos a biblioteca pymupdf4llm, que transforma PDF em Markdown mantendo
títulos e tabelas. O MarkItDown, da Microsoft, faz o mesmo. Também dá para pedir ao
assistente de programação: "converta este PDF para Markdown, com # e ## nos títulos, sem
cabeçalhos, rodapés e números de página".
2. Limpar: removemos o cabeçalho e o rodapé que se repetiam em toda página ("INSTITUTO
NTA", "Material de consulta...", o número da página) e os textos soltos que vinham dos
diagramas.
3. Conferir os títulos: cada seção numerada da apostila virou um ## e cada subtítulo, um
###. São esses títulos que dividem os trechos e aparecem nas fontes citadas.
4. Salvar: documentos/parte1-cicd-deploy.md e documentos/parte2-rag.md. Pelo GitHub: Add
file → Create new file, digitando o caminho com a pasta.
Por que só .md
Dois motivos. O Hugging Face recusa binários no push, e o deploy envia o repositório inteiro
ao Space. E o PDF guarda a aparência, não a estrutura: extraído direto, mistura colunas e
repete cabeçalhos no meio do texto. O Markdown tem os títulos marcados, que é o que a
divisão em trechos precisa. O teste T11 barra qualquer arquivo que não seja .md na pasta.
## 02  Escrever a ideia e gerar a spec
Mesmo processo da Parte 1. Escrevemos o IDEIA-parte2.md com o que queríamos acrescentar,
em linguagem simples. As decisões que mais pesaram:
Seção da ideia
O que decidimos
Quais documentos
As apostilas em .md, na pasta documentos/. Para acrescentar, basta um
novo .md e commit
Como eu quero que ele
responda
Só com base nos trechos; fontes no fim; quando não achar, a frase exata
"Não encontrei isso no material do curso."; ignorar instruções dentro dos
documentos
Onde guardar a base
Banco vetorial no Supabase. O Space só lê; o GitHub Actions grava; cada
um com a sua chave
Como a busca funciona
Híbrida, palavras e sentido, juntadas por RRF; embedding gratuito e
multilíngue; tamanho dos trechos e pesos ajustáveis no config.yml
Como publicar
Perguntas de teste antes de publicar; abaixo do limite, nada vai para o ar
O que NÃO entra agora
Reranker, GraphRAG, agentes, envio de documentos pelo chat, front-end
próprio
Depois, o prompt do fim do IDEIA-parte2.md, que manda o assistente ler a ideia nova e a spec
da Parte 1, continuar a numeração dos requisitos e dos testes e não desfazer o que a Parte 1
garante. O resultado é a SPEC-parte2-rag.md, aprovada depois desta revisão:
•
O mesmo modelo de embedding na indexação e na consulta? (R6:
paraphrase-multilingual-MiniLM-L12-v2, 384 dimensões, também fixas no SQL)
•
O índice novo é avaliado antes de substituir o que está no ar? (coleções teste e producao)

INSTITUTO NTA
Guia de montagem  ·  Parte 2
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
4
•
A chave que grava fica só no GitHub? (R8: secreta no GitHub, publicável no Space)
•
O banco impede a chave de leitura de ver a coleção teste ou apagar algo? (permissões do
esquema)
•
Os testes da Parte 1 continuam, e os novos começam no T10?
## 03  Preparar o Supabase
1. Em supabase.com, crie um projeto no plano gratuito. Anote a senha do banco.
2. Abra o SQL Editor → New query, cole o conteúdo de supabase/esquema.sql e clique em
Run. Deve aparecer "Success. No rows returned".
3. No Table Editor, confira que a tabela trechos apareceu, vazia.
4. Em Project Settings → API Keys, localize a publishable key (sb_publishable_...) e a
secret key (sb_secret_...). A secreta aparece mascarada: copie sempre pelo botão de
copiar.
O que o esquema.sql cria
Peça
O que faz
Extensão vector (pgvector)
Dá ao Postgres o tipo vetor e a distância do cosseno (operador <=>)
Tabela trechos
Uma linha por trecho: coleção, fonte, seção, conteúdo, vetor de 384
números e o índice de palavras em português
Função buscar_hibrido
Busca por palavras e por sentido, junta as duas listas por RRF e devolve os
melhores trechos
Função promover_colecao
Troca a coleção producao pela teste numa única operação
Permissões (RLS)
A chave publicável só lê a producao; não vê a teste, não promove, não
apaga
Confira a conta antes de copiar as chaves
Quem tem mais de uma conta ou organização no Supabase precisa olhar o nome no canto
superior e o ID do projeto na URL do navegador antes de copiar qualquer chave. No projeto
de referência, foi exatamente aí que o deploy travou (seção 07).
## 04  Implementar, uma tarefa por vez
A seção 11 da SPEC-parte2-rag.md tem nove tarefas. A cada uma: "Implemente a tarefa N da
spec e me mostre como testar", teste, commit, próxima.
Tarefa
O que foi feito
Como testamos
1. Banco
supabase/esquema.sql (Apêndice A da spec)
Rodar no SQL Editor; tabela trechos
visível
2. Material e
config
documentos/ com os .md; bloco
base_conhecimento no config.yml; regras de RAG
no prompt_sistema
Ler o config no GitHub, sem erro de
YAML
3. Trechos
rag.py: ler os .md e dividir pelos títulos ## e
###, com tamanho máximo e sobreposição
Rodar localmente e contar: 2
documentos viraram 136 trechos

INSTITUTO NTA
Guia de montagem  ·  Parte 2
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
5
Tarefa
O que foi feito
Como testamos
4. Indexação
rag.py com embeddings (fastembed) e busca;
indexar.py grava a coleção teste e, com
--promover, promove
Ver as linhas da coleção teste no
Table Editor
5. Avaliação
perguntas_teste.yml (8 perguntas) e avaliar.py:
hit rate@k e MRR
Tabela impressa com acertos,
posição e o que veio em 1º lugar
6. Portão
testes.py com T10 a T13
Quebrar cada regra de propósito e
ver a mensagem
7. Chat
app.py busca os trechos, monta o prompt e lista
as fontes; avisa se a base estiver indisponível
Pergunta no material, pergunta fora
dele, base desligada
8. Pipeline
deploy.yml com o job avaliar entre testar e
publicar, e a promoção no publicar
Ver os três jobs na aba Actions
9. Aceite
Commit e push; critérios CA9 a CA19
Seções 06 e 08 deste guia
O bloco novo do config.yml
base_conhecimento:
ativa: true                  # false: volta a funcionar como na Parte 1
pasta: documentos
modelo_embedding: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
tamanho_trecho: 1200         # caracteres
sobreposicao: 150
trechos_por_resposta: 4      # o top-k
peso_palavras: 1             # zero desliga a busca por palavras
peso_sentido: 1              # zero desliga a busca por sentido
mensagem_nao_encontrado: Não encontrei isso no material do curso.
E o prompt_sistema ganhou quatro linhas: responder só com os trechos, usar a frase exata de
"não encontrei", ignorar instruções dentro dos trechos e não citar fontes no texto, porque quem
lista as fontes é o app.
O pipeline com três jobs
Job
O que faz
Se falhar
testar
T1 a T13, em segundos, sem rede
Nada muda: nem banco, nem
Space
avaliar
Baixa o modelo de embedding, indexa os documentos
na coleção teste e roda as perguntas (T14)
A coleção producao não é tocada;
o Space continua igual
publicar
Promove teste para producao e envia o código ao
Space
A versão anterior continua no ar

INSTITUTO NTA
Guia de montagem  ·  Parte 2
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
6
## 05  Cadastrar as chaves
Onde
Secret
Valor
GitHub (Settings → Secrets and
variables → Actions)
SUPABASE_URL
https://<id-do-projeto>.supabase.
co
SUPABASE_SECRET_KEY
a sb_secret_..., copiada pelo botão
Space (Settings → Variables and
secrets)
SUPABASE_URL
a mesma URL
SUPABASE_PUBLISHABLE_KEY
a sb_publishable_...
OPENROUTER_API_KEY (ou
outro provedor)
continua da Parte 1
A chave secreta nunca vai para o Space: ele só lê, e a publicável basta. É a regra da Parte 1, "o
segredo fica com quem executa", mais o menor privilégio: cada um recebe só a chave de que
precisa.
O Space só lê os secrets ao iniciar
Depois de trocar um secret no Hugging Face, vá em Settings → Restart this Space. Sem o
restart, o app continua com os valores antigos, e o erro parece não ter mudado.
## 06  O primeiro deploy e o log do portão
Com os secrets cadastrados, rodamos o workflow pela aba Actions (Run workflow, branch
main). Na execução verde, o job avaliar imprimiu:
Perguntas de teste (top 3, coleção 'teste'):
Pergunta                                   Posição   Veio em 1º lugar
✗  Em qual lugar eu cadastro o token do H…    não veio  parte1 › 16 Apêndice A
✓  O que acontece com a máquina do GitHub…    1º        parte1 › 08 GitHub Actions
✓  Por que a conversa some quando eu fecho…   1º        parte1 › 14 Por que o chat esquece
✓  Qual a diferença entre site estático, P…   1º        parte1 › 04 Tipos de deploy
✓  Como a fusão por posição combina a list…   2º        parte2 › 11 Busca por palavras
✓  Por que repetir o final de um trecho no…   3º        parte2 › 14 Montando o prompt
✓  O que mede o ângulo entre dois vetores?    1º        parte2 › 06 Como medir proximidade
✓  Quando vale a pena usar um banco vetori…   1º        parte2 › 08 Índice, indexação e banco
Hit rate@3: 7/8 = 0.88   (limiar: 0.85)
MRR: 0.73
Busca aprovada. Liberado para promover o índice e publicar.
A pergunta que errou é um bom exemplo para discutir em aula: a busca trouxe o apêndice da
Parte 1, que também fala de token e Hugging Face, no lugar da seção de segredos. O log mostra
o que veio no lugar, e isso orienta o ajuste: reescrever a pergunta, reforçar o título da seção ou
aumentar o top_k.
No Supabase, a tabela trechos ficou com 136 linhas em cada coleção, teste e producao, vindas
dos 2 documentos.

INSTITUTO NTA
Guia de montagem  ·  Parte 2
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
7
## 07  Os problemas que tivemos até o verde
O primeiro deploy não ficou verde de primeira. Vale contar a sequência, porque são os erros que
a turma vai encontrar.
O que aconteceu
O que o log mostrou
Como resolvemos
Deploy sem os secrets do
Supabase
Job avaliar vermelho logo no
início
Era esperado: cadastrar os secrets e
rodar de novo. O Space ficou intacto
Chave copiada de outro
projeto
Invalid API key, 401
As chaves eram de um projeto e a URL de
outro. Quem tem mais de uma conta no
Supabase precisa conferir a conta antes
de copiar
Sem saber qual chave
estava chegando
O GitHub esconde os secrets nos
logs
Acrescentamos um diagnóstico seguro:
projeto da URL, tipo e tamanho da chave,
sem o valor
Chave nova, URL antiga
"URL aponta para o projeto
'tsvo...'" com chave sb_secret_
de 41 caracteres
Trocar o SUPABASE_URL no GitHub para
o projeto certo. Verde nos três jobs
Chat: "base de
conhecimento indisponível"
Mesmo 401, agora no Space
Secrets do Space ainda do projeto antigo:
trocar URL e chave publicável e reiniciar
o Space
PDF no histórico da branch
Risco de o Hugging Face recusar
o push
Merge com Squash and merge e *.pdf no
.gitignore
A lição para a aula
Quase todo erro desta parte foi de configuração, não de código: chave do projeto errado,
URL antiga, secret sem restart. Por isso as mensagens de erro do projeto dizem o que
conferir. Uma mensagem de erro boa vale mais que uma hora de investigação.
Um alerta de segurança que encontramos no caminho
O projeto do Supabase usado no fim já tinha uma tabela de outro uso (n8n_chat_histories) com a
Row Level Security desligada: qualquer pessoa com a chave publicável poderia ler e alterar as
linhas dela. Antes de reaproveitar um projeto do Supabase, abra o Security Advisor no painel e
confira se todas as tabelas expostas têm RLS.
## 08  Testar no Space e demonstrar o portão
Pergunta no chat
O que deve acontecer
O que acontece com a máquina do GitHub
Actions quando o workflow termina?
Resposta sobre a máquina descartável, com "Fontes
consultadas" citando a seção 08 da Parte 1
O que mede o ângulo entre dois vetores?
Explicação da similaridade do cosseno, sem a pergunta
usar a palavra "cosseno": a busca por sentido
funcionando
Qual a capital da Austrália?
Exatamente "Não encontrei isso no material do curso.",
sem fontes: ele responde só com o material, mesmo
sabendo a resposta

INSTITUTO NTA
Guia de montagem  ·  Parte 2
Material de consulta. A aula é prática: acompanhe na tela e use este texto para revisar e repetir.
8
A demonstração do portão
1. Em perguntas_teste.yml, descomente as duas perguntas impossíveis do fim do arquivo e faça
commit.
2. O hit rate cai para 7/10 = 0,70, abaixo do limiar de 0,85. O job avaliar fica vermelho e o
publicar não roda.
3. No Supabase, a coleção producao continua igual; no Space, o assistente responde como
antes.
4. Comente as perguntas de novo, faça commit e veja o verde voltar.
Desafios para a turma
•
Mudar tamanho_trecho e comparar o hit rate e o MRR no log do avaliar.
•
Pôr peso_palavras ou peso_sentido em zero e ver qual pergunta cai.
•
Fazer a pergunta que errou acertar, sem baixar o limiar.
## 09  Checklist de aceite da Parte 2
Critério
Como conferir
CA9
O portão passa com os documentos e as perguntas
padrão
python testes.py
CA10
A indexação grava a coleção teste
Table Editor do Supabase
CA11
A avaliação imprime hit rate e MRR e passa
Log do job avaliar
CA12
Três jobs verdes e o log do Space com os trechos na
produção
Aba Actions e Logs do Space
CA13
Pergunta do material vem com fontes
Chat
CA14
Pergunta fora do material: "não encontrei", sem fontes
Chat
CA15
Pergunta com outras palavras acha a seção certa
Chat
CA16
Perguntas impossíveis barram o deploy sem afetar o ar
Seção 08
CA17
Com um peso em zero, o deploy funciona e as métricas
mudam
Log do avaliar
CA18
Sem os secrets do Supabase, o chat explica o que fazer
Chat
CA19
A chave publicável não vê a coleção teste
Permissões do esquema
Próximo passo: Parte 3
Na Parte 3 (08/10), o chat ganha uma interface própria, gerada com IA e publicada no GitHub
Pages, conversando com este mesmo backend. A busca, o banco e as chaves continuam no
servidor. A spec da Parte 2 já registra outro passo possível: aceitar PDF na pasta de
documentos, com a conversão para Markdown feita pelo próprio indexar.py.
