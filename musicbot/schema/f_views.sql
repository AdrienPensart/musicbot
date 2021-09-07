drop view if exists musicbot_private.user_account;
create or replace view musicbot_private.user_account as
select u.id, u.first_name, u.last_name, a.email, u.created_at, u.updated_at
from musicbot_public.user u
inner join musicbot_private.account a on u.id = a.user_id;
