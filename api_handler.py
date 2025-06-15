
from models import MovieInfo
import requests

OMDB_API_KEY = "586ea014"  # replace with your actual OMDb API key

def fetch_movie_data(title: str) -> MovieInfo:
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["Response"] == "False":
        raise Exception(f"Movie not found: {data['Error']}")

    return MovieInfo(
        title=data["Title"],
        year=data["Year"],
        genre=data["Genre"],
        director=data["Director"],
        plot=data["Plot"],
        imdb_rating=data["imdbRating"],
        poster_url=data["Poster"]
    )

def get_featured_movies():
    featured_titles = [
        "Dune: Part Two",
        "Barbie",
        "Oppenheimer",
        "Godzilla x Kong: The New Empire"
    ]
    featured_movies = []
    for title in featured_titles:
        try:
            movie = fetch_movie_data(title)
            featured_movies.append(movie)
        except:
            continue
    return featured_movies
