insert into filters as f (name) values ('default') on conflict do nothing;
insert into filters as f (name, youtube) values ('youtube not found', 'not found') on conflict do nothing;
insert into filters as f (name, youtube) values ('no youtube links', null) on conflict do nothing;
insert into filters as f (name, min_rating, max_rating) values ('no rating', 0.0, 0.0) on conflict do nothing;
