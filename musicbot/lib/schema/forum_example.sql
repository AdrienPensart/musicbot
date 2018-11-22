--create database forum_example;
--\connect forum_example
-- postgraphile --connection postgres://forum_example_postgraphile:xyz@localhost --schema forum_example --default-role forum_example_anonymous --secret keyboard_kitten --token forum_example.jwt_token

create schema forum_example;
create schema forum_example_private;

create table forum_example.person (
    id               serial primary key,
    first_name       text not null check (char_length(first_name) < 80),
    last_name        text check (char_length(last_name) < 80),
    about            text,
    created_at       timestamp default now(),
    updated_at       timestamp default now()
);

create type forum_example.post_topic as enum ('discussion', 'inspiration', 'help', 'showcase');

create or replace function forum_example.current_person_id() returns integer as $$
    select current_setting('jwt.claims.person_id')::integer
$$ language sql stable;

create table forum_example.post (
    id               serial primary key,
    author_id        integer not null references forum_example.person(id) default forum_example.current_person_id(),
    headline         text not null check (char_length(headline) < 280),
    body             text,
    topic            forum_example.post_topic,
    created_at       timestamp default now(),
    updated_at       timestamp default now()
);

create table forum_example_private.person_account (
	person_id        integer primary key references forum_example.person(id) on delete cascade,
	email            text not null unique check (email ~* '^.+@.+\..+$'),
	password_hash    text not null
);

create extension if not exists pgcrypto;

create or replace function forum_example.register_person(
	first_name text,
	last_name text,
	email text,
	password text
) returns forum_example.person as $$
declare
    person forum_example.person;
begin
    insert into forum_example.person (first_name, last_name) values
      (first_name, last_name)
      returning * into person;

    insert into forum_example_private.person_account (person_id, email, password_hash) values
      (person.id, email, crypt(password, gen_salt('bf')));

    return person;
end;
$$ language plpgsql strict security definer;

create role forum_example_postgraphile login password 'xyz';
create role forum_example_anonymous;
grant forum_example_anonymous to forum_example_postgraphile;
create role forum_example_person;
grant forum_example_person to forum_example_postgraphile;

create type forum_example.jwt_token as (
	role text,
	person_id integer
);

create or replace function forum_example.authenticate(
	email text,
	password text
) returns forum_example.jwt_token as $$
declare
  account forum_example_private.person_account;
begin
    select a.* into account
    from forum_example_private.person_account as a
    where a.email = $1;

    if account.password_hash = crypt(password, account.password_hash) then
        return ('forum_example_person', account.person_id)::forum_example.jwt_token;
    else
        return null;
    end if;
end;
$$ language plpgsql strict security definer;

create or replace function forum_example.current_person() returns forum_example.person as $$
    select *
    from forum_example.person
    where id = current_setting('jwt.claims.person_id', true)::integer
$$ language sql stable;

alter default privileges revoke execute on functions from public;

grant usage on schema forum_example to forum_example_anonymous, forum_example_person;

grant select on table forum_example.person to forum_example_anonymous, forum_example_person;
grant update, delete on table forum_example.person to forum_example_person;

grant select on table forum_example.post to forum_example_anonymous, forum_example_person;
grant insert, update, delete on table forum_example.post to forum_example_person;
grant usage on sequence forum_example.post_id_seq to forum_example_person;

grant execute on function forum_example.authenticate(text, text) to forum_example_anonymous, forum_example_person;
grant execute on function forum_example.current_person() to forum_example_anonymous, forum_example_person;
grant execute on function forum_example.current_person_id() to forum_example_anonymous, forum_example_person;

grant execute on function forum_example.register_person(text, text, text, text) to forum_example_anonymous;

alter table forum_example.person enable row level security;
alter table forum_example.post enable row level security;

-- User permissions
create policy select_person on forum_example.person for select using (id = current_setting('jwt.claims.person_id')::integer);
create policy update_person on forum_example.person for update to forum_example_person using (id = current_setting('jwt.claims.person_id')::integer);
create policy delete_person on forum_example.person for delete to forum_example_person using (id = current_setting('jwt.claims.person_id')::integer);

-- Post permissions
create policy select_post on forum_example.post for select using (author_id = current_setting('jwt.claims.person_id')::integer);
create policy insert_post on forum_example.post for insert to forum_example_person with check (author_id = current_setting('jwt.claims.person_id')::integer);
create policy update_post on forum_example.post for update to forum_example_person using (author_id = current_setting('jwt.claims.person_id')::integer);
create policy delete_post on forum_example.post for delete to forum_example_person using (author_id = current_setting('jwt.claims.person_id')::integer);
