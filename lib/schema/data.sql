insert into filters as f (name) values ('default') on conflict do nothing;
insert into filters as f (name, youtubes) values ('youtube not found', '{not found}') on conflict do nothing;
insert into filters as f (name, youtubes) values ('no youtube links', '{}') on conflict do nothing;
insert into filters as f (name, min_rating, max_rating) values ('no rating', 0.0, 0.0) on conflict do nothing;
insert into filters as f (name, min_rating, no_keywords) values ('best (4.0+)', 4.0, '{cutoff,bad,demo,intro}') on conflict do nothing;
insert into filters as f (name, min_rating, no_keywords) values ('best (4.5+)', 4.5, '{cutoff,bad,demo,intro}') on conflict do nothing;
insert into filters as f (name, min_rating, no_keywords) values ('best (5.0+)', 5.0, '{cutoff,bad,demo,intro}') on conflict do nothing;
insert into filters as f (name, no_keywords) values ('no live', '{live}') on conflict do nothing;
insert into filters as f (name, keywords) values ('only live', '{live}') on conflict do nothing;
