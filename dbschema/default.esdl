module default {
    abstract type Entity {
        required property name -> str;
        required property created_at -> datetime {
            default := std::datetime_current();
            readonly := true;
        }
        required property updated_at -> datetime {
            default := std::datetime_current();
        }
    }

    scalar type Rating extending float32 {
        constraint one_of (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0);
    }

    scalar type Size extending int64 {
        constraint min_value(0);
    }

    scalar type Length extending int64 {
        constraint min_value(0);
    }

    type Artist extending Entity {
        overloaded required property name -> str {
            constraint exclusive;
        }
        multi link albums := .<artist[is Album];
        link musics := (select .albums.musics);
        link keywords := (select .musics.keywords);
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating), 2));
        property length := (select sum(.musics.length));
        property duration := (select to_duration(seconds := <float64>.length));
    }

    type Album extending Entity {
        required link artist -> Artist {
            on target delete delete source;
        }
        constraint exclusive on ( (.name, .artist ) );

        multi link musics := .<album[is Music];
        property length := (select sum(.musics.length));
        property duration := (select to_duration(seconds := <float64>.length));
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating), 2));
        link keywords := (select .musics.keywords);
    }

    type Music extending Entity {
        multi property links -> str;
        required property rating -> Rating {
            default := 0.0
        }
        required property length -> Length;
        property duration := (select to_duration(seconds := <float64>.length));
        required property size -> Size;
        property track -> int16;

        required link album -> Album {
            on target delete delete source;
        }
        link artist := (select .album.artist);

        required link genre -> Genre {
            on target delete delete source;
        }

        multi link keywords -> Keyword;

        constraint exclusive on ( (.name, .album ) );
    }

    type Keyword extending Entity {
        overloaded required property name -> str {
            constraint exclusive;
        }
        multi link musics := .<keywords[is Music];
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating), 2));
    }

    type Genre extending Entity {
        overloaded required property name -> str {
            constraint exclusive;
        }
        multi link musics := .<genre[is Music];
        property rating := (select <float64>round(<decimal>math::mean(.musics.rating), 2));
        link keywords := (select .musics.keywords);
        property length := (select sum(.musics.length));
        property duration := (select to_duration(seconds := <float64>.length));
    }
}

using extension graphql;
using extension edgeql_http;
