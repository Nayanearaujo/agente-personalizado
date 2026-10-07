# SPEC: Parte 2, RAG e base de conhecimento da NOA

**Status:** proposta para aprovação, sem implementação do RAG.

**Projeto:** NOA Engenharia de Dados. **GitHub:** `Nayanearaujo/agente-personalizado`. **Space:** `oaraujo/noa-engenharia-de-dados`.

Esta especificação acrescenta a Aula 2 ao projeto existente. Parte de `IDEIA-parte2.md`, da spec da Parte 1 e das apostilas anexadas. As decisões iniciais foram confirmadas: material disponível, parâmetros do professor e uso gratuito. A conta no Supabase ainda não existe.

## 1. Objetivo, público e escopo

A NOA recupera trechos de documentos antes de responder e mostra suas fontes. O público continua sendo quem estuda Engenharia de Dados, Estatística e Machine Learning.

A primeira base contém as duas apostilas do curso, convertidas para Markdown e revisadas. Isso permite responder sobre CI/CD, deploy, RAG, vetores e embeddings. Assuntos sem cobertura, como inferência estatística e regressão, precisam de documentos próprios antes de serem respondidos no modo RAG. O guia de montagem orienta a implementação, sem entrar automaticamente como documento de consulta.

Entram indexação, Supabase, busca híbrida, referências e avaliação da recuperação. Não entram reranker, GraphRAG, agentes adicionais, envio de documentos pelo chat, histórico no banco, avaliação automática do texto gerado ou front-end próprio. A Parte 3 fica para depois. O layout compacto e a coruja permanecem.

**Dependência conhecida:** o Space inicia, mas a chamada real ao modelo ainda não foi aprovada no teste de resposta. Construção e avaliação da busca não dependem dela. O aceite da resposta gerada continua pendente até uma chamada real funcionar. RAG não corrige acesso ao provedor.

## 2. Stack e onde cada peça roda

| Peça | Escolha | Onde roda |
|---|---|---|
| Aplicação | Python 3.12 e Gradio, preservando as versões da Parte 1 | Space |
| Embeddings | FastEmbed, `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensões | CPU do Actions e do Space |
| Banco | Supabase Free, Postgres com pgvector | Supabase |
| Palavras | Full-text search do Postgres, configuração `portuguese`, `websearch_to_tsquery` e `ts_rank_cd` | Supabase |
| Significado | Distância do cosseno, operador `<=>`, busca exata para a base pequena | Supabase |
| Fusão | RRF ponderada, constante 60, posições começando em 1 | Supabase |
| Indexação e avaliação | Scripts Python e cliente `supabase` | GitHub Actions |
| Geração | Roteador existente, somente modelos OpenRouter `:free` | Space |

Full-text search do Postgres não será chamado de BM25. A biblioteca e suas dependências terão versões compatíveis com Python 3.12 fixadas na implementação, após verificar instalação. O modelo será carregado uma vez por processo, com cache. Não depende de GPU nem de chave de API. Indexação e consulta devem compartilhar versão e configuração do modelo; alteração exige reindexação.

## 3. Arquivos novos e alterados

| Arquivo | Mudança |
|---|---|
| `IDEIA-parte2.md`, `SPEC-parte2-rag.md` | Documentação desta etapa |
| `documentos/parte1-cicd-deploy.md`, `documentos/parte2-rag.md` | Texto revisado das apostilas, com títulos de seção |
| `supabase/esquema.sql` | SQL descrito na seção 8 |
| `agente/rag.py` | Leitura, divisão, embeddings, recuperação e montagem do contexto |
| `scripts/indexar.py` | Reconstrói teste; promoção explícita depois da avaliação |
| `scripts/avaliar.py` | Hit rate e MRR, relatório e código de saída |
| `perguntas_teste.yml` | Oito perguntas com arquivo e seção esperados |
| `tests/test_rag.py`, `tests/test_avaliacao.py` | Verificações sem serviços reais |
| `agente/config.py`, `config.yaml` | Contrato novo, compatível com a Parte 1 |
| `agente/interface.py` | Consulta antes do roteador, fontes ao fim, mesmo layout |
| `agente/segredos.py`, `scripts/procurar_chaves.py` | Reconhecimento e limpeza de chaves Supabase |
| `scripts/publicar.py` | Inclui módulo RAG e confere nomes dos secrets necessários |
| `requirements.txt`, `requirements-dev.txt` | Dependências e versões verificadas |
| `.github/workflows/deploy.yml` | Job avaliar e promoção controlada |
| `README.md`, `.gitignore` | Uso da base, comandos e exclusão de PDFs/cache |

O projeto usa `config.yaml`, não `config.yml`. Não criaremos um segundo arquivo. Também manteremos módulos em `agente/` e scripts em `scripts/`, seguindo a estrutura real do professor usada na Parte 1.

## 4. Contrato dos novos campos

Bloco raiz opcional `base_conhecimento`. Ausente significa desativado, para manter compatibilidade com os testes e configurações da Parte 1. Na configuração da NOA, será ativado apenas depois da preparação do banco.

| Campo no bloco | Obrigatório | Valores | Padrão |
|---|---|---|---|
| `ativa` | Não | Booleano, sem aspas | `false` |
| `pasta` | Não | Caminho relativo dentro do repositório, sem `..` e sem links que escapem da raiz | `documentos` |
| `modelo_embedding` | Não | ID MiniLM da seção 2, única opção nesta etapa | ID da seção 2 |
| `tamanho_trecho` | Não | Inteiro de 200 a 2000 caracteres | `1200` |
| `sobreposicao` | Não | Inteiro de 0 até tamanho menos 1 | `150` |
| `trechos_por_resposta` | Não | Inteiro de 1 a 10 | `4` |
| `peso_palavras` | Não | Número finito de 0 a 10 | `1` |
| `peso_sentido` | Não | Número finito de 0 a 10 | `1` |
| `similaridade_minima` | Não | Número de 0 a 1, limiar semântico inicial a calibrar com testes negativos | `0.5` |
| `mensagem_nao_encontrado` | Não | Frase exata exigida pela aula | `Não encontrei isso no material do curso.` |

Campos desconhecidos, repetidos, tipos errados e chaves no YAML continuam sendo erros. Os dois pesos não podem ser zero juntos. Peso zero elimina aquela modalidade, inclusive o cálculo do embedding se sentido estiver desligado.

O limite em caracteres não substitui o limite de tokens do modelo: a divisão também verifica o tokenizer e subdivide textos que seriam truncados. Não indexar embeddings de apenas uma fração silenciosamente cortada do trecho.

Um top-k sempre pode devolver algo, mesmo para uma pergunta sem relação. Por isso, candidatos vetoriais precisam superar o limiar semântico; candidatos lexicais precisam ter correspondência. RRF é ordenação, não probabilidade de resposta. Os testes negativos e a instrução de insuficiência continuam necessários, sem garantia matemática de eliminar alucinações.

## 5. Requisitos funcionais, a partir de RF23

- **RF23:** carregar o bloco opcional sem invalidar a configuração anterior. Desativado mantém o comportamento da Parte 1.
- **RF24:** ler somente `.md` na pasta configurada; recusar arquivo vazio, falta de título, caminho inseguro ou qualquer outro tipo.
- **RF25:** dividir por títulos, preservar arquivo e seção, manter tamanho e sobreposição válidos. O mesmo conteúdo e configuração geram os mesmos IDs de trechos.
- **RF26:** gerar vetores finitos de 384 dimensões usando o mesmo modelo para documentos e perguntas; carregar o modelo sob demanda sem rede nos testes unitários.
- **RF27:** indexar somente a coleção teste, identificada pelo SHA da execução. Falha parcial não permite avaliação aprovada nem promoção.
- **RF28:** buscar palavras e significado, filtrar candidatos e combinar por RRF ponderada. Empates usam ID como desempate estável.
- **RF29:** o Space usa somente a chave publicável e só enxerga produção. A chave de escrita nunca entra no Space.
- **RF30:** avaliar perguntas reais contra teste, conferindo arquivo e seção. Publicar somente quando o hit rate atingir o limiar.
- **RF31:** promover atomicamente somente a versão avaliada e aprovada. Avaliação reprovada não altera produção ou Space.
- **RF32:** enviar os trechos como dados delimitados. Documentos e histórico não substituem instruções de sistema nem autorizam ferramentas.
- **RF33:** responder apenas com apoio suficiente no contexto. Sem candidatos, devolver a frase exata diretamente, sem chamar IA. Se o modelo reconhecer insuficiência, normalizar a mesma frase e não anexar fontes.
- **RF34:** listar ao fim as fontes consultadas, arquivo e seção, extraídas dos metadados recuperados, sem referências inventadas pelo modelo. A lista mostra o material fornecido, não comprova cada afirmação da resposta.
- **RF35:** erro de banco ou embedding produz aviso de base indisponível, sem fingir que não encontrou e sem responder por conhecimento geral.
- **RF36:** preservar streaming, limites de pergunta, mensagens de falha, proteção de chaves, layout e restrição a modelos gratuitos. Fontes aparecem apenas após resposta bem-sucedida ou texto efetivamente gerado, nunca junto de erro de provedor.
- **RF37:** registrar métricas e diagnósticos seguros, sem perguntas de visitantes, chaves ou texto documental nos logs do chat. As perguntas de avaliação são públicas e podem aparecer no relatório do CI.

## 6. Portão de verificações

A Parte 1 deste repositório já ocupa **T1 a T17**. A apostila da Parte 2 usa T10 a T14 em outra base. Mantemos ambos os nomes na correspondência, sem apagar ou renumerar verificações antigas.

| NOA | Equivalente da aula | Verificação |
|---|---|---|
| T18 | T10 | Configuração RAG válida, mensagem e regras do contexto |
| T19 | T11 | Pasta com Markdown válido, títulos, conteúdo e caminhos seguros |
| T20 | T12 | Perguntas, limiar, arquivo e seção esperados válidos |
| T21 | T13 | Varredura de chaves Supabase em arquivos e histórico |
| T22 | T14 | Avaliação real no banco: hit rate@3 mínimo 0.85 e MRR registrado |
| T23 | Complemento | Chunking, limite do tokenizer, RRF, pesos zero, fontes e ausência simulada |
| T24 | Complemento | Isolamento de teste, negação de escrita e promoção para chave publicável |
| T25 | Complemento | SHA avaliado igual ao promovido, indexação parcial ou coleção vazia barradas |

T18 a T21, T23 e T25 usam simulações e não precisam de credenciais reais. T22 e a conferência de permissões de T24 usam o projeto preparado. Os testes anteriores continuam rodando integralmente. A suíte não faz chamadas reais ao OpenRouter.

## 7. Pipeline, indexação, avaliação e promoção

1. **testes:** em branches e PRs, roda as verificações anteriores e as novas sem banco ou IA real.
2. **avaliar:** apenas na main, após testes, baixa o modelo, reconstrói teste com SHA da execução, verifica contagem completa e executa as oito perguntas. Publica relatório com posições, hit rate@3 e MRR. Produção não é alterada.
3. **publicar:** exige avaliação aprovada para o mesmo SHA, confere configuração do Space, promove teste em transação e envia o pacote. Acompanha o build como na Parte 1.

Uma única execução da main pode ocupar avaliação e publicação por vez. A trava de concorrência deve abranger os dois jobs, e não somente o upload, para evitar que outra execução substitua teste durante a avaliação. PRs de forks não recebem secrets. As execuções não são canceladas no meio da promoção.

Se teste ou avaliação falhar, o Space e produção ficam intactos. Promoção de banco e publicação no Hugging Face são sistemas separados, portanto não formam uma única transação. Antes de promover, guardar uma cópia privada da produção anterior e sua versão no banco. Se o upload/build falhar, restaurar a coleção anterior em transação; se essa restauração falhar, o job precisa avisar explicitamente. A cópia anterior não fica em artefato público. O contrato do modelo permanece o mesmo para que o app anterior não receba vetores incompatíveis.

O índice de teste permanece disponível para inspeção depois da avaliação. Novas execuções reconstruirão teste. Nenhuma promoção ocorre automaticamente pela aplicação do Space.

## 8. SQL do banco e permissões

O SQL abaixo é o contrato proposto para `supabase/esquema.sql`, não uma alteração já aplicada. Usar um projeto novo para a NOA. A chave publicável usa o papel `anon`; a secreta de servidor usa `service_role`. RLS limita leitura à produção e permissões SQL negam escrita aos visitantes. As funções usam `security invoker`, respeitando o papel chamador.

```sql
create schema if not exists extensions;
create extension if not exists vector with schema extensions;

create table public.trechos (
  id text primary key,
  colecao text not null check (colecao in ('teste', 'producao', 'anterior')),
  versao text not null,
  fonte text not null,
  secao text not null,
  conteudo text not null check (length(conteudo) > 0),
  embedding extensions.vector(384) not null,
  palavras tsvector generated always as
    (to_tsvector('portuguese', conteudo)) stored
);
create index trechos_palavras on public.trechos using gin (palavras);
create index trechos_colecao on public.trechos (colecao, versao);
alter table public.trechos enable row level security;
create policy ler_producao on public.trechos
  for select to anon, authenticated using (colecao = 'producao');
revoke all on public.trechos from public, anon, authenticated;
grant select on public.trechos to anon, authenticated;
grant all on public.trechos to service_role;

create function public.buscar_hibrido(
  p_texto text, p_vetor extensions.vector(384),
  p_colecao text default 'producao', p_k integer default 4,
  p_peso_palavras double precision default 1,
  p_peso_sentido double precision default 1,
  p_sim_min double precision default 0.5
) returns table (id text, fonte text, secao text, conteudo text,
                 pontuacao double precision)
language sql stable security invoker
set search_path = public, extensions, pg_temp
as $$
  with lex as (
    select t.id, row_number() over (
      order by ts_rank_cd(t.palavras,
        websearch_to_tsquery('portuguese', p_texto)) desc, t.id) pos
    from public.trechos t
    where t.colecao = p_colecao and p_peso_palavras > 0
      and t.palavras @@ websearch_to_tsquery('portuguese', p_texto)
    order by pos limit 20
  ), sem as (
    select t.id, row_number() over (
      order by t.embedding <=> p_vetor, t.id) pos
    from public.trechos t
    where t.colecao = p_colecao and p_peso_sentido > 0
      and p_vetor is not null
      and 1 - (t.embedding <=> p_vetor) >= p_sim_min
    order by pos limit 20
  ), unidos as (
    select coalesce(l.id, s.id) id,
      coalesce(p_peso_palavras / (60.0 + l.pos), 0) +
      coalesce(p_peso_sentido / (60.0 + s.pos), 0) score
    from lex l full outer join sem s using (id)
  )
  select t.id, t.fonte, t.secao, t.conteudo, u.score::double precision
  from unidos u join public.trechos t on t.id = u.id
  order by u.score desc, t.id limit greatest(1, least(p_k, 10));
$$;

create function public.promover_colecao(p_versao text)
returns void language plpgsql security invoker
set search_path = public, extensions, pg_temp
as $$
begin
  lock table public.trechos in exclusive mode;
  if not exists (select 1 from public.trechos
                 where colecao = 'teste' and versao = p_versao)
     or exists (select 1 from public.trechos
                where colecao = 'teste' and versao <> p_versao) then
    raise exception 'Coleção de teste ausente ou de outra versão';
  end if;
  delete from public.trechos where colecao = 'anterior';
  insert into public.trechos
    (id, colecao, versao, fonte, secao, conteudo, embedding)
    select 'anterior:' || id, 'anterior', versao, fonte, secao, conteudo, embedding
    from public.trechos where colecao = 'producao';
  delete from public.trechos where colecao = 'producao';
  insert into public.trechos
    (id, colecao, versao, fonte, secao, conteudo, embedding)
    select 'producao:' || id, 'producao', versao, fonte, secao, conteudo, embedding
    from public.trechos where colecao = 'teste';
end;
$$;

create function public.restaurar_colecao(p_versao_publicada text)
returns void language plpgsql security invoker
set search_path = public, extensions, pg_temp
as $$
begin
  lock table public.trechos in exclusive mode;
  if exists (select 1 from public.trechos where colecao = 'producao'
             and versao <> p_versao_publicada) then
    raise exception 'Produção foi alterada por outra execução';
  end if;
  delete from public.trechos where colecao = 'producao';
  insert into public.trechos
    (id, colecao, versao, fonte, secao, conteudo, embedding)
    select substr(id, length('anterior:') + 1), 'producao', versao,
           fonte, secao, conteudo, embedding
    from public.trechos where colecao = 'anterior';
end;
$$;

revoke all on function public.buscar_hibrido(text, extensions.vector,
  text, integer, double precision, double precision, double precision)
  from public;
grant execute on function public.buscar_hibrido(text, extensions.vector,
  text, integer, double precision, double precision, double precision)
  to anon, authenticated, service_role;
revoke all on function public.promover_colecao(text) from public, anon, authenticated;
revoke all on function public.restaurar_colecao(text) from public, anon, authenticated;
grant execute on function public.promover_colecao(text) to service_role;
grant execute on function public.restaurar_colecao(text) to service_role;
```

Na indexação, IDs começam com `teste:` e incluem hash do arquivo, seção, posição e conteúdo. A indexação elimina apenas teste; nunca usa truncamento da tabela inteira. A promoção mantém teste para inspeção e copia seus registros para produção. A cópia anterior permite restauração até na primeira publicação, quando o índice anterior está vazio. A promoção não mede qualidade: o pipeline é responsável por chamar a função somente depois do relatório aprovado.

O esquema deve ser executado uma vez; mudanças posteriores usam migração explícita, sem apagar índices existentes. Conferir o schema da extensão no projeto novo. Na tarefa do banco, testar as políticas com o papel real de leitura, não apenas com o SQL Editor administrativo.

| Onde | Nome | Uso |
|---|---|---|
| GitHub Actions, secret | `SUPABASE_URL` | URL do projeto correto |
| GitHub Actions, secret | `SUPABASE_SECRET_KEY` | Escrita, avaliação, promoção e restauração |
| Space, secret | `SUPABASE_URL` | Mesma URL |
| Space, secret | `SUPABASE_PUBLISHABLE_KEY` | Somente leitura de produção |
| GitHub, secret existente | `HF_TOKEN` | Publicar o pacote |
| Space, secret existente | `OPENROUTER_API_KEY` | Gerar respostas, como na Parte 1 |

Preferir chaves novas `sb_secret_...` e `sb_publishable_...`. Não copiar valores para o chat, código ou Markdown. A varredura deve abranger também chaves legadas no formato JWT. Reiniciar o Space após alterar secrets. Uma chave publicável consultando `teste` deve receber zero linhas; escrita e promoção devem ser negadas.

## 9. Perguntas e métricas

Formato proposto, com um exemplo. Os títulos esperados serão conferidos contra o Markdown revisado antes de preencher o arquivo definitivo.

```yaml
top_k: 3
limiar_hit_rate: 0.85
perguntas:
  - pergunta: "O que mede o ângulo entre dois vetores?"
    fonte_esperada: "parte2-rag.md"
    secao_esperada: "06 Como medir proximidade: produto escalar e cosseno"
```

Serão oito perguntas positivas, quatro de cada apostila, incluindo formulações literais e paráfrases. Temas: segredos, máquina do Actions, histórico, deploy, cosseno, RRF, sobreposição e banco vetorial. Cada pergunta aponta para arquivo e seção existentes.

**Hit rate@3:** perguntas com fonte e seção corretas nas três primeiras posições, dividido pelo total. Com oito perguntas e limiar 0.85, é necessário acertar pelo menos sete: 7/8 = 0.875. Sem arredondar antes da comparação.

**MRR@3:** média de `1/posição` do primeiro trecho correto entre os três primeiros, ou zero se não encontrado. Informativa nesta versão, sem limiar próprio. A avaliação usa top 3; o chat recebe até quatro trechos. O log explicita essa diferença.

Perguntas fora do acervo, como capital de país, ficam em casos negativos separados, sem fonte inventada. Para demonstrar a reprovação, usar duas perguntas com resposta ausente que apontem para arquivos e seções válidos, porém sem relação. A validação estrutural passa, a avaliação falha e a produção permanece intacta. Executar essa demonstração apenas após termos uma versão boa publicada.

## 10. Critérios de aceite

- [ ] CA13: todos os testes anteriores continuam passando e o layout aprovado permanece.
- [ ] CA14: documentos convertidos, títulos conferidos, nenhum PDF ou dado sigiloso no repositório.
- [ ] CA15: Supabase mostra trechos, fontes, seções e vetores de 384 dimensões.
- [ ] CA16: chave publicável lê produção, não lê teste/anterior e não escreve nem promove.
- [ ] CA17: oito perguntas avaliadas, hit rate@3 >= 0.85 e MRR@3 exibido.
- [ ] CA18: perguntas impossíveis barram promoção e publicação, preservando a versão no ar.
- [ ] CA19: paráfrase encontra a seção certa; pesos zero funcionam separadamente.
- [ ] CA20: pergunta com apoio suficiente recebe resposta didática e fontes reais.
- [ ] CA21: pergunta sem apoio retorna a frase exata, sem fontes.
- [ ] CA22: indisponibilidade do banco é distinguida de ausência de informação.
- [ ] CA23: instruções maliciosas em trechos não mudam o papel do assistente nos testes de prompt.
- [ ] CA24: secrets separados, logs limpos e modelos pagos recusados.
- [ ] CA25: teste de falha de deploy após promoção restaura o índice anterior.

CA20 depende de o provedor de geração responder. Não marcar esse item como concluído com uma resposta simulada. Simulações verificam comportamento do código, não disponibilidade real do modelo.

## 11. Implementação, uma tarefa por vez

| Tarefa | Entrega | Como testar |
|---|---|---|
| 1 | Conta/projeto Supabase gratuito e esquema SQL | Ver tabela e funções; conferir RLS e permissões de leitura/escrita |
| 2 | Markdown das duas apostilas e contrato RAG desativado inicialmente | Revisar títulos; validar YAML e toda suíte anterior |
| 3 | Leitura e divisão em trechos | Conferir fontes, seções, limites, sobreposição e IDs determinísticos |
| 4 | Embeddings, busca e indexação de teste | Ver vetores e contagem no painel; testar chave publicável |
| 5 | Oito perguntas, avaliação e relatório | Conferir posições, hit rate e MRR calculados à mão em casos pequenos |
| 6 | Portão e varredura ampliados | Introduzir erro controlado em cópia temporária e verificar bloqueio |
| 7 | Integração com chat e fontes | Testes simulados; pergunta real quando o provedor estiver disponível |
| 8 | Pipeline, promoção e restauração | Main com três jobs; demonstrar reprovação sem alterar produção |
| 9 | Aceite e documentação | Percorrer checklist; registrar pendências reais sem mascarar falhas |

A tarefa 1 inclui orientação de criação da conta. Escolher plano Free, sem contratar serviço ou cadastrar cobrança para este trabalho. Cada tarefa termina com instruções de teste e revisão antes da próxima. Não ativar RAG no Space enquanto o banco, as chaves e a coleção de produção não estiverem preparados.

## 12. Erros comuns e referências

| Sintoma | Conferir |
|---|---|
| 401 no banco | URL e chave pertencem ao mesmo projeto e chave foi copiada integralmente |
| Função não encontrada | SQL executado no projeto correto; assinatura e schema das funções |
| Vetor com dimensão errada | Modelo idêntico nos dois lados; não substituir sem migrar e reindexar |
| Busca encontra algo para toda pergunta | Limiar e teste negativo; top-k sozinho não indica relevância |
| Hit rate baixo | Título/seção, conversão, divisão e paráfrases; não baixar o limiar para esconder erro |
| Chave de leitura vê teste | Política RLS e função invoker; não usar secret key no Space |
| Base indisponível no Space | Secrets corretos, projeto ativo e reinício após troca |
| OpenRouter falha apesar da busca boa | Falha de geração independente; não trocar para modelo pago |
| Primeira consulta lenta | Download/cache e carga inicial do embedding |
| Publicação falha após promoção | Restauração do índice anterior e diagnóstico separado do build |

Referências de implementação: apostila Parte 2 e guia de montagem anexados; spec da Parte 1 deste repositório; [modelos suportados pelo FastEmbed](https://qdrant.github.io/fastembed/examples/Supported_Models/); [funções do Supabase](https://supabase.com/docs/guides/database/functions); [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security).

**Próximo passo após aprovação:** implementar a tarefa 1 e mostrar como testar. Esta proposta não cria conta, banco, credenciais ou chamadas pagas.
