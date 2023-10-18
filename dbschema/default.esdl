module default {
    function bytes_to_human(size: int64, k: int64 = 1000, decimals: int64 = 2, units: array<str> = [' B', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB', ' ZB', ' YB']) -> str {
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
        required name: str {
            constraint exclusive;
        }
        required created_at: datetime {
            default := std::datetime_current();
            readonly := true;
        }
        required updated_at: datetime {
            rewrite insert, update using (datetime_of_statement())
        }
        multi link albums := .<artist[is Album];
        link musics := (select .albums.musics);
        link keywords := (select .musics.keywords);
        link genres := (select .musics.genre);
        property size := (select sum(.musics.size));
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating), 2));
        property length := (select sum(.musics.length));
        property duration := (select to_duration(seconds := <float64>.length));
        property human_size := (select bytes_to_human(.size));
        property human_duration := (select to_str(.duration, "HH24:MI:SS"));
        property all_keywords := (select to_str(array_agg((select Artist.keywords.name order by Artist.keywords.name)), " "));
        property all_genres := (select to_str(array_agg(.musics.genre.name), " "));
        property n_albums := (select count(.albums));
        property n_musics := (select count(.musics));
    }

    type Album {
        required name: str;
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
        property length := (select sum(.musics.length));
        property size := (select sum(.musics.size));
        property duration := (select to_duration(seconds := <float64>.length));
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating), 2));
        link keywords := (select .musics.keywords);

        constraint exclusive on ((.name, .artist));
        index on ((.name, .artist));
    }

    type Folder {
        required name: str;
        required created_at: datetime {
            default := std::datetime_current();
            readonly := true;
        }
        required updated_at: datetime {
            rewrite insert, update using (datetime_of_statement())
        }

        required user: str;
        required ipv4: str;
        multi link musics := .<folders[is Music];

        constraint exclusive on ((.name, .ipv4));
        index on ((.name, .ipv4));
    }

    # define a local music
    type Music {
        required name: str;
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
        property duration := (select to_duration(seconds := <float64>.length));
        required size: Size;
        track: Track;

        required link album: Album {
            on target delete delete source;
        }
        link artist := (select .album.artist);

        required link genre: Genre {
            on target delete delete source;
        }

        # youtube: str;
        # spotify: str;

        multi keywords: Keyword;
        multi folders: Folder {
            path: str;
        }
        property paths := (select .folders@path);

        constraint exclusive on ((.name, .album));
        index on ((.name, .album));
    }

    type Keyword {
        required name: str {
            constraint exclusive;
        }
        required created_at: datetime {
            default := std::datetime_current();
            readonly := true;
        }
        required updated_at: datetime {
            rewrite insert, update using (datetime_of_statement())
        }

        multi link musics := .<keywords[is Music];
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating), 2));
    }

    type Genre {
        required name: str {
            constraint exclusive;
        }
        required created_at: datetime {
            default := std::datetime_current();
            readonly := true;
        }
        required updated_at: datetime {
            rewrite insert, update using (datetime_of_statement())
        }

        multi link musics := .<genre[is Music];
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating), 2));
        link keywords := (select .musics.keywords);
        property length := (select sum(.musics.length));
        property duration := (select to_duration(seconds := <float64>.length));
    }
    alias artists := (
        select Artist {
            *,
            human_size,
            human_duration,
            all_keywords,
            all_genres,
            n_albums,
            n_musics
        } order by .name
    );
}

using extension graphql;
using extension edgeql_http;
