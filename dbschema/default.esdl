module default {
    # abstract type Entity {
    #     required name: str;
    #     required created_at: datetime {
    #         default := std::datetime_current();
    #         readonly := true;
    #     }
    #     required updated_at: datetime {
    #         rewrite insert, update using (datetime_of_statement())
    #     }
    # }

    scalar type Rating extending float32 {
        constraint one_of (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0);
    }

    scalar type Size extending int64 {
        constraint min_value(0);
    }

    scalar type Length extending int64 {
        constraint min_value(0);
    }

    scalar type `Limit` extending int64 {
        constraint min_value(0);
    }

    # type Artist extending Entity {
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
        # overloaded required name: str {
        #     constraint exclusive;
        # }
        multi link albums := .<artist[is Album];
        link musics := (select .albums.musics);
        link keywords := (select .musics.keywords);
        link genres := (select .musics.genre);
        property size := (select sum(.musics.size));
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating), 2));
        property length := (select sum(.musics.length));
        property duration := (select to_duration(seconds := <float64>.length));
    }

    # type Album extending Entity {
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

    # type Folder extending Entity {
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
    # type Music extending Entity {
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
        track: int16;

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

    # type Keyword extending Entity {
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

        # overloaded required name: str {
        #     constraint exclusive;
        # }
        multi link musics := .<keywords[is Music];
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating), 2));
    }

    # type Genre extending Entity {
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
        # overloaded required name: str {
        #     constraint exclusive;
        # }

        multi link musics := .<genre[is Music];
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating), 2));
        link keywords := (select .musics.keywords);
        property length := (select sum(.musics.length));
        property duration := (select to_duration(seconds := <float64>.length));
    }
}

using extension graphql;
using extension edgeql_http;
