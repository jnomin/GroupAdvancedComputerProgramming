# scraper.py
import requests
from bs4 import BeautifulSoup
import tempfile
import shutil

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_imdb_id(movie_title: str) -> str:
    slug = movie_title.strip().lower().replace(" ", "_")
    first_letter = slug[0]
    suggestion_url = f"https://v2.sg.media-imdb.com/suggestion/{first_letter}/{slug}.json"

    try:
        response = requests.get(suggestion_url, headers=HEADERS, timeout=10)
        data = response.json()

        if "d" in data and len(data["d"]) > 0:
            imdb_id = data["d"][0].get("id", "")
            print(f"[✅] IMDb ID found: {imdb_id}")
            return imdb_id
        else:
            print(f"[❌] No IMDb ID found for '{movie_title}'")
            return ""
    except Exception as e:
        print(f"[💥] IMDb ID fetch failed: {e}")
        return ""

def get_imdb_reviews(movie_title: str) -> list:
    imdb_id = fetch_imdb_id(movie_title)
    if not imdb_id:
        return []

    reviews_url = f"https://www.imdb.com/title/{imdb_id}/reviews"
    print(f"[🌐] Scraping: {reviews_url}")

    try:
        response = requests.get(reviews_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        review_blocks = soup.select(".text.show-more__control")
        if not review_blocks:
            review_blocks = soup.select(".review-container .content .text")
        if not review_blocks:
            review_blocks = soup.select(".ipc-html-content")

        print(f"[📝] Found {len(review_blocks)} reviews.")
        reviews = [r.get_text(strip=True) for r in review_blocks if r.get_text(strip=True)]
        return reviews

    except Exception as e:
        print(f"[💥] Scraping error: {e}")
        return []

def download_poster(url):
    try:
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            return None, "Failed to fetch image"

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, tmp)
        tmp.close()
        return tmp.name, None
    except Exception as e:
        return None, str(e)
