module default {
    # global current_user := (
    #     assert_single((
    #         select User { id, name }
    #         filter .identity = global ext::auth::ClientTokenIdentity
    #     ))
    # );

    # type User {
    #     required name: str;
    #     required identity: ext::auth::Identity;
    # }

    # alias MATCH_ALL := "(.*?)";

    function bytes_to_human(
        size: int64,
        k: int64 = 1000,
        decimals: int64 = 2,
        units: array<str> = [' B', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB', ' ZB', ' YB'],
    ) -> str {
        using (
            select '0' ++ units[0] if size = 0
            else (
                with i := <int64>math::floor(math::ln(math::abs(size)) / math::ln(k))
                select to_str(std::round(<decimal>(size / k ^ i), decimals)) ++ units[i]
            )
        );
        annotation title := "Convert a byte size to human readable string";
    };

    scalar type Rating extending float64 {
        constraint one_of (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0);
    }

    scalar type Size extending int64 {
        constraint min_value(0);
    }

    scalar type Length extending int64 {
        constraint min_value(0);
    }

    scalar type Track extending int64;

    scalar type `Limit` extending int64 {
        constraint min_value(0);
    }

    type Artist {
        # required user: User;
        required name: str;
        required created_at: datetime {
            default := std::datetime_current();
            readonly := true;
        }
        required updated_at: datetime {
            rewrite insert, update using (datetime_of_statement())
        }
        multi link albums := .<artist[is Album];
        property n_albums := (select count(.albums));

        link musics := (select .albums.musics);
        property n_musics := (select count(.musics));
        property length := (select sum(.musics.length));
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating ?? {0.0}), 2));
        property all_genres := (select to_str(array_agg(.musics.genre.name), " "));

        link keywords := (select .musics.keywords);
        property all_keywords := (select to_str(array_agg((select Artist.keywords.name order by Artist.keywords.name)), " "));

        link genres := (select .musics.genre);
        property n_genres := (select count(.genres));

        property size := (select sum(.musics.size));
        property human_size := (select bytes_to_human(.size));

        property duration := (select to_duration(seconds := <float64>.length));
        property human_duration := (select to_str(.duration, "HH24:MI:SS"));

        constraint exclusive on ((.name));

        index fts::index on (
           fts::with_options(
              .name,
              language := fts::Language.eng,
           )
        );

    }

    type Album {
        # required user: User;
        required name: str;
        property title := (select .artist.name ++ " - " ++ .name);
        required created_at: datetime {
            default := std::datetime_current();
            readonly := true;
        }
        required updated_at: datetime {
            rewrite insert, update using (datetime_of_statement())
        }

        required link artist: Artist {
            on target delete delete source;
        }

        multi link musics := .<album[is Music];
        property n_musics := (select count(.musics));
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating ?? {0.0}), 2));
        property length := (select sum(.musics.length));

        property duration := (select to_duration(seconds := <float64>.length));
        property human_duration := (select to_str(.duration, "HH24:MI:SS"));

        property size := (select sum(.musics.size));
        property human_size := (select bytes_to_human(.size));

        link keywords := (select .musics.keywords);
        property all_keywords := (select to_str(array_agg((select Artist.keywords.name order by Artist.keywords.name)), " "));

        link genres := (select .musics.genre);
        property n_genres := (select count(.genres));
        property all_genres := (select to_str(array_agg(.musics.genre.name), " "));

        constraint exclusive on ((.name, .artist));

        index fts::index on (
           fts::with_options(
              .name,
              language := fts::Language.eng
           )
        );
    }

    type Folder {
        # required user: User;
        required name: str;
        required username: str;
        required created_at: datetime {
            default := std::datetime_current();
            readonly := true;
        }
        required updated_at: datetime {
            rewrite insert, update using (datetime_of_statement())
        }

        required ipv4: str;

        multi link musics := .<folders[is Music];
        property n_musics := (select count(.musics));
        property length := (select sum(.musics.length));

        link keywords := (select .musics.keywords);
        property n_keywords := (select count(.keywords));
        property all_keywords := (select to_str(array_agg((select Artist.keywords.name order by Artist.keywords.name)), " "));

        property duration := (select to_duration(seconds := <float64>.length));
        property human_duration := (select to_str(.duration, "HH24:MI:SS"));

        property size := (select sum(.musics.size));
        property human_size := (select bytes_to_human(.size));

        link artists := (select .musics.artist);
        property n_artists := (select count(.artists));
        property all_artists := (select to_str(array_agg(.musics.artist.name), " "));

        link albums := (select .musics.album);
        property n_albums := (select count(.albums));

        link genres := (select .musics.genre);
        property n_genres := (select count(.genres));
        property all_genres := (select to_str(array_agg(.musics.genre.name), " "));

        constraint exclusive on ((.name, .username, .ipv4));

        index fts::index on (
           fts::with_options(
              .name,
              language := fts::Language.eng,
           )
        );
    }

    # define a local music
    type Music {
        # required user: User;
        required name: str;
        property title := (select .album.title ++ " - " ++ .name);
        required created_at: datetime {
            default := std::datetime_current();
            readonly := true;
        }
        required updated_at: datetime {
            rewrite insert, update using (datetime_of_statement())
        }

        required rating: Rating {
            default := 0.0
        }
        required length: Length;
        track: Track;

        property duration := (select to_duration(seconds := <float64>.length));
        property human_duration := (select to_str(.duration, "HH24:MI:SS"));

        required size: Size;
        property human_size := (select bytes_to_human(.size));

        required link album: Album {
            on target delete delete source;
        }
        link artist := (select .album.artist);

        required link genre: Genre;

        # youtube: str;
        # spotify: str;

        multi keywords: Keyword;
        required multi folders: Folder {
            path: str;
        }
        property paths := (select .folders@path);

        constraint exclusive on ((.name, .album));

        index fts::index on (
           fts::with_options(
              .name,
              language := fts::Language.eng,
           )
        );
    }

    type Keyword {
        # required user: User;
        required name: str;
        required created_at: datetime {
            default := std::datetime_current();
            readonly := true;
        }
        required updated_at: datetime {
            rewrite insert, update using (datetime_of_statement())
        }

        multi link musics := .<keywords[is Music];
        property n_musics := (select count(.musics));
        property length := (select sum(.musics.length));
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating ?? {0.0}), 2));

        link artists := (select .musics.artist);
        property n_artists := (select count(.artists));
        property all_artists := (select to_str(array_agg(.musics.artist.name), " "));

        link albums := (select .musics.album);
        property n_albums := (select count(.albums));

        property duration := (select to_duration(seconds := <float64>.length));
        property human_duration := (select to_str(.duration, "HH24:MI:SS"));

        property size := (select sum(.musics.size));
        property human_size := (select bytes_to_human(.size));

        constraint exclusive on ((.name));

        index fts::index on (
           fts::with_options(
              .name,
              language := fts::Language.eng,
           )
        );
    }

    type Genre {
        # required user: User;
        required name: str;
        required created_at: datetime {
            default := std::datetime_current();
            readonly := true;
        }
        required updated_at: datetime {
            rewrite insert, update using (datetime_of_statement())
        }

        multi link musics := .<genre[is Music];
        property n_musics := (select count(.musics));
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating ?? {0.0}), 2));

        link artists := (select .musics.artist);
        property n_artists := (select count(.artists));
        property all_artists := (select to_str(array_agg(.musics.artist.name), " "));

        link albums := (select .musics.album);
        property n_albums := (select count(.albums));

        link keywords := (select .musics.keywords);
        property length := (select sum(.musics.length));

        property duration := (select to_duration(seconds := <float64>.length));
        property human_duration := (select to_str(.duration, "HH24:MI:SS"));

        property size := (select sum(.musics.size));
        property human_size := (select bytes_to_human(.size));

        constraint exclusive on ((.name));

        index fts::index on (
           fts::with_options(
              .name,
              language := fts::Language.eng,
           )
        );
    }

    function gen_playlist(
        named only min_length: Length = 0,
        named only max_length: Length = 2147483647,
        named only min_size: Size = 0,
        named only max_size: Size = 2147483647,
        named only min_rating: Rating = 0.0,
        named only max_rating: Rating = 5.0,
        named only artist: str = "(.*?)",
        named only album: str = "(.*?)",
        named only genre: str = "(.*?)",
        named only title: str = "(.*?)",
        named only keyword: str = "(.*?)",
        named only `limit`: `Limit` = 2147483647,
        named only pattern: str = "",
    ) -> set of Music {
        using (
            select Music
            filter
                .length >= min_length and .length <= max_length
                and .size >= min_size and .size <= max_size
                and .rating >= min_rating and .rating <= max_rating
                and re_test(artist, .artist.name)
                and re_test(album, .album.name)
                and re_test(genre, .genre.name)
                and re_test(title, .name)
                and re_test(keyword, array_join(array_agg((select .keywords.name)), " "))
                and (pattern = "" or ext::pg_trgm::word_similar(pattern, .title))
            order by
                .artist.name then
                .album.name then
                .track then
                .name
            limit `limit`
        );
        annotation title := "Generate a playlist from parameters";
    };
}

using extension graphql;
using extension edgeql_http;
using extension pg_trgm;
# using extension auth;
