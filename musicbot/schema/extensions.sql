create extension if not exists "hstore";
create extension if not exists "pg_trgm";
create extension if not exists "uuid-ossp";
create extension if not exists "pg_stat_statements";
--ex :
--create table forum_example.person (
--  id uuid primary key default uuid_generate_v1mc(),
--  ...
--);
create extension if not exists "pgcrypto";
create extension if not exists "pgjwt";
