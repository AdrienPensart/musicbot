from sanic_wtf import SanicForm
from wtforms import IntegerField, BooleanField, SelectField, SelectMultipleField, SubmitField
from ..filter import Filter

rating_choices = [(x * 0.5, x * 0.5) for x in range(0, 11)]
formats_choices = [(x, x) for x in Filter.formats]


class FilterForm(SanicForm):
    shuffle = BooleanField(label="Shuffle?", default=False)
    youtube = SelectField(label='YouTube', default="2", choices=[("2", "Yes and No"), ("1", "Yes"), ("0", "No")])

    min_rating = SelectField(label='Minimum rating', default=0.0, choices=rating_choices, coerce=float)
    max_rating = SelectField(label='Maximum rating', default=5.0, choices=rating_choices, coerce=float)

    formats = SelectMultipleField(label='Formats', default=[], choices=formats_choices)
    no_formats = SelectMultipleField(label='No formats', default=[], choices=formats_choices)

    limit = IntegerField(label='Limit', default=2147483647)

    min_duration = IntegerField(label='Min duration', default=0)
    max_duration = IntegerField(label='Max duration', default=2147483647)

    min_size = IntegerField(label='Min size', default=0)
    max_size = IntegerField(label='Max size', default=2147483647)

    genres = SelectMultipleField(label='Genres', default=[], choices=[])
    no_genres = SelectMultipleField(label='No genres', default=[], choices=[])

    artists = SelectMultipleField(label='Artists', default=[], choices=[])
    no_artists = SelectMultipleField(label='No artists', default=[], choices=[])

    keywords = SelectMultipleField(label='Keywords', default=[], choices=[])
    no_keywords = SelectMultipleField(label='No keywords', default=[], choices=[])

    titles = SelectMultipleField(label='Titles', default=[], choices=[])
    no_titles = SelectMultipleField(label='No titles', default=[], choices=[])

    albums = SelectMultipleField(label='Albums', default=[], choices=[])
    no_albums = SelectMultipleField(label='No albums', default=[], choices=[])

    progressive = SubmitField(label='Progressive')
    generate = SubmitField(label='Generate')

    def initialize(self, records):
        genres_choices = [(x, x) for x in records['genres']]
        no_genres_choices = genres_choices
        self.genres.choices = genres_choices
        self.no_genres.choices = no_genres_choices

        artists_choices = [(x, x) for x in records['artists']]
        self.artists.choices = artists_choices
        self.no_artists.choices = artists_choices

        keywords_choices = [(x, x) for x in records['keywords']]
        self.keywords.choices = keywords_choices
        self.no_keywords.choices = keywords_choices

        titles_choices = [(x, x) for x in records['titles']]
        self.titles.choices = titles_choices
        self.no_titles.choices = titles_choices

        albums_choices = [(x, x) for x in records['albums']]
        self.albums.choices = albums_choices
        self.no_albums.choices = albums_choices

    # def __init__(self, records, precedent, *args, **kwargs):
    #     # only_csrf = MultiDict([('csrf_token', precedent.get('csrf_token'))])
    #     # super(FlaskForm, self).__init__(only_csrf, *args, **kwargs)
    #     # super(SanicForm, self).__init__(precedent, *args, **kwargs)
