create table if not exists musicbot_public.link
(
    id         serial primary key,
    user_id    integer not null references musicbot_public.user (id) on delete cascade default musicbot_public.current_musicbot(),
    music_id   integer not null references musicbot_public.music (id) on delete cascade,
    url        text not null,
    created_at   timestamp with time zone default now(),
    updated_at   timestamp with time zone default now(),
    constraint unique_music_link unique (url, music_id, user_id) deferrable
);

create index if not exists link_user_idx on musicbot_public.link (user_id);
create index if not exists link_music_idx on musicbot_public.link (music_id);

alter table if exists musicbot_public.link enable row level security;
alter table if exists musicbot_public.link force row level security;

grant usage on sequence musicbot_public.link_id_seq to musicbot_user;

grant select on table musicbot_public.link to musicbot_anonymous, musicbot_user;
grant insert, update, delete on table musicbot_public.link to musicbot_user;

drop policy if exists insert_link on musicbot_public.link cascade;
create policy insert_link on musicbot_public.link for insert with check (user_id = musicbot_public.current_musicbot());

drop policy if exists select_link on musicbot_public.link cascade;
create policy select_link on musicbot_public.link for select using (user_id = musicbot_public.current_musicbot());

drop policy if exists update_link on musicbot_public.link cascade;
create policy update_link on musicbot_public.link for update using (user_id = musicbot_public.current_musicbot());

drop policy if exists delete_link on musicbot_public.link cascade;
create policy delete_link on musicbot_public.link for delete using (user_id = musicbot_public.current_musicbot());
