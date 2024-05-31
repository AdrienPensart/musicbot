for keyword in (
    select Keyword {name}
    filter contains(array_agg(.musics.keywords.name), 'pike') and .musics.rating >= 4.0 and .musics.album.artist.name = 'Buckethead'
)
union (keyword.name) except {'pike'}
