from dataclasses import dataclass

@dataclass
class MovieInfo:
    title: str
    year: str
    genre: str
    director: str
    plot: str
    imdb_rating: str
    poster_url: str