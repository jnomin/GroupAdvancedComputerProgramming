import requests
import json
import time
import os
from datetime import datetime

TMDB_API_KEY = "c9c1635c535e8f0aed729f4fb42ac2e9"
OMDB_API_KEY = "586ea014"

def fetch_omdb_rating(title, year):
    url = f"http://www.omdbapi.com/?t={title}&y={year}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("Response") == "True":
            return {
                "imdb_rating": data.get("imdbRating"),
                "plot": data.get("Plot"),
                "imdb_id": data.get("imdbID"),
                "imdb_url": f"https://www.imdb.com/title/{data.get('imdbID')}/"
            }
    except:
        return {}
    return {}

def get_trending_movies(api_key=TMDB_API_KEY, limit=20):
    filepath = "static/featured_today.json"
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)[:limit]

    url = "https://api.themoviedb.org/3/trending/movie/day"
    params = {"api_key": api_key}
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, params=params, headers=headers)
    trending = []

    if response.status_code == 200:
        movies = response.json().get("results", [])[:limit]
        for m in movies:
            title = m.get("title")
            year = m.get("release_date", "")[:4]
            tmdb_movie = {
                "title": title,
                "year": year,
                "poster_path": m.get("poster_path"),
                "tmdb_rating": m.get("vote_average"),
                "tmdb_id": m.get("id")
            }
            omdb_data = fetch_omdb_rating(title, year)
            trending.append({**tmdb_movie, **omdb_data})
            time.sleep(0.2)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(trending, f, ensure_ascii=False, indent=2)

    return trending[:limit]

def get_top_mongolian_movies(api_key=TMDB_API_KEY, limit=100):
    filepath = "static/mongolian_movies.json"
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)[:limit]

    headers = {"User-Agent": "Mozilla/5.0"}
    mongolian_movies = []
    page = 1

    while len(mongolian_movies) < limit:
        params = {
            "api_key": api_key,
            "with_original_language": "mn",
            "sort_by": "vote_average.desc",
            "page": page
        }
        try:
            res = requests.get("https://api.themoviedb.org/3/discover/movie", params=params, headers=headers)
            if res.status_code != 200:
                print(f"TMDb error on page {page}: {res.status_code}")
                break

            movies = res.json().get("results", [])
            if not movies:
                break

            for m in movies:
                if len(mongolian_movies) >= limit:
                    break
                title = m.get("title")
                year = m.get("release_date", "")[:4]
                tmdb_movie = {
                    "title": title,
                    "year": year,
                    "poster_path": m.get("poster_path"),
                    "tmdb_rating": m.get("vote_average"),
                    "tmdb_id": m.get("id")
                }
                omdb_data = fetch_omdb_rating(title, year)
                mongolian_movies.append({**tmdb_movie, **omdb_data})
                time.sleep(0.2)

            page += 1
        except Exception as e:
            print("Error:", e)
            break

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(mongolian_movies, f, ensure_ascii=False, indent=2)

    return mongolian_movies[:limit]

def get_popular_people(api_key=TMDB_API_KEY, limit=30):
    headers = {"User-Agent": "Mozilla/5.0"}
    people = []
    page = 1

    while len(people) < limit:
        try:
            url = f"https://api.themoviedb.org/3/person/popular"
            params = {"api_key": api_key, "language": "en-US", "page": page}
            res = requests.get(url, params=params, headers=headers)
            if res.status_code != 200:
                break

            for person in res.json().get("results", []):
                people.append({
                    "name": person["name"],
                    "profile_path": person.get("profile_path"),
                    "tmdb_id": person["id"],
                    "popularity": person["popularity"]
                })
                if len(people) >= limit:
                    break
        except Exception as e:
            print("Error on page", page, ":", e)
            break
        page += 1

    with open("static/popular_people.json", "w", encoding="utf-8") as f:
        json.dump(people, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(people)} most popular people.")
    return people

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    print("🔁 Downloading Featured Today...")
    featured = get_trending_movies(limit=20)
    print(f"✅ Saved {len(featured)} featured movies.")

    print("🔁 Downloading Top Mongolian Movies...")
    mongolian = get_top_mongolian_movies(limit=100)
    print(f"✅ Saved {len(mongolian)} Mongolian movies.")

    print("🔁 Downloading Most Popular People...")
    popular = get_popular_people(limit=30)
    print(f"✅ Saved {len(popular)} most popular people.")
