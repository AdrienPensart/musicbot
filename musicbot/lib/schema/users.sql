begin;

alter default privileges revoke execute on functions from public;

create table if not exists public.user (
    id               serial primary key,
    first_name       text not null check (char_length(first_name) < 80),
    last_name        text check (char_length(last_name) < 80),
    about            text,
    created_at       timestamp default now(),
    updated_at       timestamp default now()
);
alter table if exists public.user enable row level security;

drop policy if exists select_user on public.user cascade;
create policy select_user on public.user for select using (true);

drop policy if exists update_user on public.user cascade;
create policy update_user on public.user for update to musicbot_user
  using (id = current_setting('jwt.claims.user_id')::integer);

drop policy if exists delete_user on public.user cascade;
create policy delete_user on public.user for delete to musicbot_user
  using (id = current_setting('jwt.claims.user_id')::integer);

create table if not exists private.account (
    user_id          integer primary key references public.user(id) on delete cascade,
    email            text not null unique check (email ~* '^.+@.+\..+$'),
    password_hash    text not null
);

do $$
begin
    create role musicbot_postgraphile login password 'musicbot_postgraphile_password';
    exception when duplicate_object then
    raise notice 'not creating role musicbot_postgraphile -- it already exists';
end
$$;

do $$
begin
    create role musicbot_anonymous;
    exception when duplicate_object then
    raise notice 'not creating role musicbot_anonymous -- it already exists';
end
$$;

do $$
begin
    create role musicbot_user;
    exception when duplicate_object then
    raise notice 'not creating role musicbot_user -- it already exists';
end
$$;

grant musicbot_anonymous to musicbot_postgraphile;
grant musicbot_user to musicbot_postgraphile;

drop type if exists public.jwt_token cascade;
create type public.jwt_token as (
    role text,
    user_id integer
);

create or replace function public.register_user(
    first_name text,
    last_name text,
    email text,
    password text
)
returns public.user as
$$
declare
    u public.user;
begin
  insert into public.user (first_name, last_name) values
    (first_name, last_name)
    returning * into u;

  insert into private.account (user_id, email, password_hash) values
    (u.id, email, crypt(password, gen_salt('bf')));

  return u;
end;
$$ language plpgsql strict security definer;

create or replace function public.authenticate(
  email text,
  password text
)
returns jwt_token as
$$
declare
  token_information jwt_token;
  account private.account;
begin
  select a.* into account
  from private.account as a
  where a.email = $1;

  if account.password_hash = crypt(password, account.password_hash) then
    return ('musicbot_user', account.user_id)::public.jwt_token;
  else
    return null;
  end if;
end;
$$ language plpgsql strict security definer;

create or replace function public.current_musicbot()
returns public.user as
$$
  select *
  from public.user
  where id = current_setting('jwt.claims.user_id')::integer
$$ language sql stable;

grant usage on schema public to musicbot_anonymous, musicbot_user;
grant select on table public.user to musicbot_anonymous, musicbot_user;
grant update, delete on table public.user to musicbot_user;
grant execute on function public.authenticate(text, text) to musicbot_anonymous, musicbot_user;
grant execute on function public.current_musicbot() to musicbot_anonymous, musicbot_user;
grant execute on function public.register_user(text, text, text, text) to musicbot_anonymous;

end;
