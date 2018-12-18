-- execute with
-- sudo -H -u postgres bash -c 'psql -f ./main.sql'

--\connect postgres
--
--select pg_terminate_backend(pg_stat_activity.pid) from pg_stat_activity where pg_stat_activity.datname = 'musicbot_prod' and pid <> pg_backend_pid();
--
--drop database if exists musicbot_prod;
--create database musicbot_prod;
--
--\connect musicbot_prod

create schema if not exists musicbot_public;
create schema if not exists musicbot_private;
