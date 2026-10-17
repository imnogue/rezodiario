-- =====================================================================
-- Rezo Diario · base de datos en Supabase
-- Cómo usarlo: Supabase → tu proyecto → SQL Editor → New query →
-- pega todo este archivo → Run. Solo hay que hacerlo una vez.
-- =====================================================================

-- ---------- Velas del muro de intenciones ----------
create table if not exists public.velas (
  id          uuid primary key default gen_random_uuid(),
  texto       text not null default '' check (char_length(texto) <= 160),
  nombre      text not null default '' check (char_length(nombre) <= 30),
  cat         text not null default 'otra' check (cat in ('salud','familia','difuntos','estudios','trabajo','gracias','otra')),
  privada     boolean not null default false,
  visitante   text not null check (char_length(visitante) between 4 and 64),
  created_at  timestamptz not null default now(),
  oculta      boolean not null default false,
  reportes    int not null default 0
);
create index if not exists velas_created_idx on public.velas (created_at desc);

-- Oraciones «He rezado por ti» (una por visitante y vela)
create table if not exists public.rezos (
  vela_id    uuid not null references public.velas(id) on delete cascade,
  visitante  text not null check (char_length(visitante) between 4 and 64),
  created_at timestamptz not null default now(),
  primary key (vela_id, visitante)
);

-- Avisos de intenciones inadecuadas (uno por visitante y vela)
create table if not exists public.avisos (
  vela_id    uuid not null references public.velas(id) on delete cascade,
  visitante  text not null,
  created_at timestamptz not null default now(),
  primary key (vela_id, visitante)
);

alter table public.velas  enable row level security;
alter table public.rezos  enable row level security;
alter table public.avisos enable row level security;

-- Cualquiera puede encender una vela, pero no leer la tabla directamente
drop policy if exists "encender velas" on public.velas;
create policy "encender velas" on public.velas for insert to anon, authenticated
  with check (oculta = false and reportes = 0 and created_at > now() - interval '5 minutes' and (privada = false or texto = ''));

drop policy if exists "rezar por una vela" on public.rezos;
create policy "rezar por una vela" on public.rezos for insert to anon, authenticated with check (true);

grant insert on public.velas, public.rezos to anon, authenticated;

-- Límite anti-spam: máximo 5 velas cada 10 minutos por visitante
create or replace function public.limitar_velas() returns trigger language plpgsql as $$
begin
  if (select count(*) from public.velas where visitante = new.visitante and created_at > now() - interval '10 minutes') >= 5 then
    raise exception 'Has alcanzado el límite de velas. Espera unos minutos.';
  end if;
  return new;
end $$;
drop trigger if exists limitar_velas on public.velas;
create trigger limitar_velas before insert on public.velas for each row execute function public.limitar_velas();

-- Lo que ve la web: velas de los últimos 7 días, sin ocultas y sin el texto de las privadas
create or replace view public.velas_semana as
  select v.id,
         case when v.privada then '' else v.texto end as texto,
         v.nombre, v.cat, v.privada, v.created_at,
         (select count(*) from public.rezos r where r.vela_id = v.id)::int as rezos
  from public.velas v
  where not v.oculta and v.created_at > now() - interval '7 days';
grant select on public.velas_semana to anon, authenticated;

-- Avisar de una vela: con 3 avisos se oculta sola (la puedes revisar en Table Editor → velas)
create or replace function public.reportar_vela(p_vela uuid, p_visitante text) returns void
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  insert into public.avisos (vela_id, visitante) values (p_vela, left(p_visitante, 64)) on conflict do nothing;
  select count(*) into n from public.avisos where vela_id = p_vela;
  update public.velas set reportes = n, oculta = (n >= 3) where id = p_vela;
end $$;
grant execute on function public.reportar_vela(uuid, text) to anon, authenticated;

-- ---------- Cuentas: progreso de cada persona ----------
create table if not exists public.progreso (
  user_id    uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  datos      jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
alter table public.progreso enable row level security;
drop policy if exists "ver mi progreso" on public.progreso;
create policy "ver mi progreso" on public.progreso for select to authenticated using (auth.uid() = user_id);
drop policy if exists "crear mi progreso" on public.progreso;
create policy "crear mi progreso" on public.progreso for insert to authenticated with check (auth.uid() = user_id);
drop policy if exists "actualizar mi progreso" on public.progreso;
create policy "actualizar mi progreso" on public.progreso for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
grant select, insert, update on public.progreso to authenticated;

-- ---------- Moderación rápida ----------
-- Ver las velas con avisos:   select * from velas where reportes > 0 order by created_at desc;
-- Volver a mostrar una vela:  update velas set oculta = false, reportes = 0 where id = '...';
-- Borrar una vela:            delete from velas where id = '...';
