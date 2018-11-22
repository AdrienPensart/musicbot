--select pg_terminate_backend(pg_stat_activity.pid) from pg_stat_activity where pg_stat_activity.datname = 'musicbot_prod' and pid <> pg_backend_pid();
--drop schema if exists musicbot_private cascade;
--drop schema if exists musicbot_public  cascade;
--drop database if exists musicbot_prod;

--drop database if exists forum_example;

--drop extension if exists pgcrypto cascade;

--drop schema if exists forum_example cascade;
--drop schema if exists forum_example_private cascade;

--drop role if exists forum_example_postgraphile;
--drop role if exists forum_example_anonymous;
--drop role if exists forum_example_person;
