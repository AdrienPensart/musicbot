create or replace function musicbot_public.current_musicbot_id() returns integer as $$
    select current_setting('jwt.claims.user_id')::integer
$$ language sql stable;

create table if not exists musicbot_public.user (
    id               serial primary key,
    first_name       text not null check (char_length(first_name) < 80),
    last_name        text check (char_length(last_name) < 80),
    created_at       timestamp with time zone default now(),
    updated_at       timestamp with time zone default now()
);
alter table if exists musicbot_public.user enable row level security;

create table if not exists musicbot_private.account (
    user_id          integer primary key references musicbot_public.user(id) on delete cascade,
    email            text not null unique check (email ~* '^.+@.+\..+$'),
    password_hash    text not null
);

--drop role if exists musicbot_anonymous;
--create role musicbot_anonymous;
do $$
begin
    create role musicbot_anonymous;
    exception when duplicate_object then
    raise notice 'not creating role musicbot_anonymous -- it already exists';
end
$$;

--drop role if exists musicbot_user;
--create role musicbot_user;
do $$
begin
    create role musicbot_user;
    exception when duplicate_object then
    raise notice 'not creating role musicbot_user -- it already exists';
end
$$;

--drop role if exists musicbot_postgraphile;
--create role musicbot_postgraphile login password 'musicbot_postgraphile_password';
do $$
begin
    create role musicbot_postgraphile login password 'musicbot_postgraphile_password';
    exception when duplicate_object then
    raise notice 'not creating role musicbot_postgraphile -- it already exists';
end
$$;

grant musicbot_anonymous to musicbot_postgraphile;
grant musicbot_user to musicbot_postgraphile;

drop type if exists musicbot_public.jwt_token cascade;
create type musicbot_public.jwt_token as (
    role text,
    user_id integer
);

create or replace function musicbot_public.register_user(
    first_name text,
    last_name text,
    email text,
    password text
)
returns musicbot_public.user as
$$
    with insert_user as (
        insert into musicbot_public.user as u (first_name, last_name)
		values (first_name, last_name)
        returning *
	), insert_account as (
        insert into musicbot_private.account (user_id, email, password_hash)
        values ((select insert_user.id from insert_user), email, crypt(password, gen_salt('bf')))
	)
	select insert_user.* from insert_user;
$$ language sql strict security definer;

create or replace function musicbot_public.remove_user(
    _email text
)
returns boolean as
$$
    with d as (
		delete from musicbot_public.user u
		using musicbot_private.account a
		where u.id = a.user_id and a.email = _email
		returning *
	) select (coalesce(count(*), 0) > 0) as c from d;
$$ language sql strict security definer;

create or replace function musicbot_public.authenticate(
  email text,
  password text
)
returns musicbot_public.jwt_token as
$$
declare
  token_information musicbot_public.jwt_token;
  account musicbot_private.account;
begin
    select a.* into account
    from musicbot_private.account as a
    where a.email = $1;

    if account.password_hash = crypt(password, account.password_hash) then
		set role musicbot_user;
		--set local jwt.claims.role to 'musicbot_user';
		set session authorization musicbot_user;
		perform set_config('jwt.claims.role', 'musicbot_user', false);
		perform set_config('jwt.claims.user_id', account.user_id::text, false);
        return ('musicbot_user', account.user_id)::musicbot_public.jwt_token;
    else
        raise notice 'Authentication failed for user %', email;
        return null;
    end if;
end;
$$ language plpgsql;
--$$ language plpgsql strict security definer;

create or replace function musicbot_public.new_token(
  email text,
  password text,
  secret text
)
returns text as
$$
    select sign((select row_to_json(info) from (select * from musicbot_public.authenticate(email, password) limit 1) info), secret) as token
$$ language sql stable;

create or replace function musicbot_public.current_musicbot()
returns musicbot_public.user as
$$
    select *
    from musicbot_public.user
    where id = musicbot_public.current_musicbot_id()
$$ language sql stable;

alter default privileges revoke execute on functions from public;

grant usage on schema musicbot_public to musicbot_anonymous, musicbot_user;
grant select on table musicbot_public.user to musicbot_anonymous, musicbot_user;
grant update, delete on table musicbot_public.user to musicbot_user;
grant execute on function musicbot_public.authenticate to musicbot_anonymous, musicbot_user;
grant execute on function musicbot_public.new_token to musicbot_anonymous, musicbot_user;
grant execute on function musicbot_public.current_musicbot to musicbot_anonymous, musicbot_user;
grant execute on function musicbot_public.register_user to musicbot_anonymous;
grant execute on function musicbot_public.remove_user to musicbot_user;

drop policy if exists select_user on musicbot_public.user cascade;
create policy select_user on musicbot_public.user for select to musicbot_user using (id = musicbot_public.current_musicbot_id());

drop policy if exists update_user on musicbot_public.user cascade;
create policy update_user on musicbot_public.user for update to musicbot_user using (id = musicbot_public.current_musicbot_id());

drop policy if exists delete_user on musicbot_public.user cascade;
create policy delete_user on musicbot_public.user for delete to musicbot_user using (id = musicbot_public.current_musicbot_id());