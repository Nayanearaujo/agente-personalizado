-- Esquema inicial já executado no painel. Não repetir em um banco preparado.
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
