begin;

select * from musicbot_public.register_user(first_name := 'Foo', last_name  := 'Bar', email := 'test@new.com', password   := '123456');
select * from musicbot_public.authenticate(email := 'test@new.com', password := '123456');
select * from musicbot_public.upsert();
select * from musicbot_public.upsert();

rollback;
