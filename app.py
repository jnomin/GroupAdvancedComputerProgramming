from flask import Flask, render_template, request, send_file, jsonify
from api_handler import fetch_movie_data
from scraper import get_imdb_reviews
from sentiment import analyze_sentiment
from exporter import save_as_pdf, save_as_csv
from featured_scraper import get_trending_movies, get_top_mongolian_movies
import requests
import json
import os
import time

app = Flask(__name__)
TMDB_API_KEY = "c9c1635c535e8f0aed729f4fb42ac2e9"

def summarize_sentiment(reviews):
    scores = [analyze_sentiment(r)['compound'] for r in reviews]
    return round(sum(scores) / len(scores), 3) if scores else 0.0

def sentiment_label(score):
    if score >= 0.5:
        return "Positive 😊"
    elif score <= -0.3:
        return "Negative 😠"
    return "Neutral 😐"

@app.route("/", methods=["GET", "POST"])
def index():
    movie, reviews, sentiment, error = None, [], None, None

    try:
        trending = get_trending_movies(api_key=TMDB_API_KEY, limit=20)
    except Exception as e:
        trending = []
        print("Error loading trending movies:", e)

    try:
        mongolian_movies = get_top_mongolian_movies(limit=20)
    except Exception as e:
        mongolian_movies = []
        print("Error loading Mongolian movies:", e)

    try:
        with open("static/popular_people.json", encoding="utf-8") as f:
            popular_people = json.load(f)[:10]
    except:
        popular_people = []

    if request.method == "POST":
        title = request.form.get("title")
        try:
            movie = fetch_movie_data(title)
            raw_reviews = get_imdb_reviews(title)
            if not raw_reviews:
                raise Exception("No reviews found.")
            sentiment = summarize_sentiment(raw_reviews)
            reviews = [(r, sentiment_label(analyze_sentiment(r)["compound"])) for r in raw_reviews]
        except Exception as e:
            error = str(e)

    return render_template("index.html",
                           movie=movie,
                           reviews=reviews,
                           sentiment=sentiment,
                           error=error,
                           featured=trending,
                           mongolian_movies=mongolian_movies,
                           born_today=popular_people)

@app.route("/popular-actors")
def popular_actors():
    try:
        with open("static/popular_people.json", encoding="utf-8") as f:
            people = json.load(f)[:30]
        return render_template("born_today.html", people=people)
    except Exception as e:
        return render_template("born_today.html", people=[], error=str(e))

@app.route("/featured/all")
def all_featured():
    try:
        trending = get_trending_movies(api_key=TMDB_API_KEY, limit=100)
        return render_template("featured_all.html", featured=trending)
    except Exception as e:
        return render_template("featured_all.html", featured=[], error=str(e))

@app.route("/mongolian/all")
def all_mongolian():
    try:
        mongolian_movies = get_top_mongolian_movies(limit=100)
        return render_template("see_all_mongolian.html", movies=mongolian_movies)
    except Exception as e:
        return render_template("see_all_mongolian.html", movies=[], error=str(e))

@app.route("/movie/<title>")
def movie_detail(title):
    try:
        movie = fetch_movie_data(title)
        raw_reviews = get_imdb_reviews(title)
        sentiment = summarize_sentiment(raw_reviews)
        reviews = [(r, sentiment_label(analyze_sentiment(r)["compound"])) for r in raw_reviews]
        reviews_json = json.dumps(reviews)
        return render_template("movie_detail.html", movie=movie, reviews=reviews, sentiment=sentiment, reviews_json=reviews_json)
    except Exception as e:
        return render_template("movie_detail.html", movie=None, error=str(e))

@app.route("/autocomplete")
def autocomplete():
    query = request.args.get("query")
    if not query:
        return jsonify([])
    tmdb_url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": query, "include_adult": False}
    try:
        res = requests.get(tmdb_url, params=params)
        results = res.json().get("results", [])[:7]
        return jsonify([{
            "title": m["title"],
            "year": m.get("release_date", "")[:4],
            "poster": f"https://image.tmdb.org/t/p/w92{m['poster_path']}" if m.get("poster_path") else "",
            "id": m["id"]
        } for m in results])
    except Exception as e:
        print("Autocomplete error:", e)
        return jsonify([])

@app.route("/analyze-review", methods=["POST"])
def analyze_review():
    try:
        data = request.get_json()
        review = data.get("review", "")
        if not review:
            return jsonify({"error": "Empty review"}), 400

        sentiment = analyze_sentiment(review)
        label = sentiment_label(sentiment["compound"])
        return jsonify({"label": label})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/export/chart-pdf")
def export_chart_pdf():
    import matplotlib.pyplot as plt
    from fpdf import FPDF

    title = request.args.get("title")
    if not title:
        return "Missing title"

    try:
        movie = fetch_movie_data(title)
        raw_reviews = get_imdb_reviews(title)

        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for r in raw_reviews:
            label = sentiment_label(analyze_sentiment(r)["compound"])
            sentiment_counts[label.split()[0]] += 1

        labels = sentiment_counts.keys()
        values = sentiment_counts.values()
        colors = ['#4caf50', '#ffc107', '#f44336']

        folder = os.path.join("static", "downloads")
        os.makedirs(folder, exist_ok=True)

        chart_path = os.path.join(folder, f"{title.replace(' ', '_')}_pie.png")
        plt.figure(figsize=(4, 4))
        plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors)
        plt.title("Sentiment Distribution")
        plt.savefig(chart_path)
        plt.close()

        pdf_path = os.path.join(folder, f"{title.replace(' ', '_')}_report.pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"{movie.title} ({movie.year})", ln=True)
        pdf.cell(200, 10, txt=f"Genre: {movie.genre}", ln=True)
        pdf.cell(200, 10, txt=f"Director: {movie.director}", ln=True)
        pdf.cell(200, 10, txt=f"IMDb Rating: {movie.imdb_rating}/10", ln=True)
        pdf.ln(10)
        pdf.image(chart_path, x=30, y=None, w=150)
        pdf.output(pdf_path)

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return f"Failed to generate chart PDF: {e}", 500

@app.route("/export/csv")
def export_csv():
    title = request.args.get("title")
    if not title:
        return "Missing title"
    try:
        raw_reviews = get_imdb_reviews(title)
        reviews = [(r, sentiment_label(analyze_sentiment(r)["compound"])) for r in raw_reviews]
        save_as_csv("movie_reviews.csv", reviews)
        return send_file("movie_reviews.csv", as_attachment=True)
    except Exception as e:
        return f"Failed to export CSV: {str(e)}"

@app.route("/download-poster")
def download_poster():
    url = request.args.get("url")
    if not url:
        return "Missing poster URL", 400
    try:
        title = request.args.get("title", "poster").replace(" ", "_")
        timestamp = int(time.time())
        folder = os.path.join(os.getcwd(), "static", "downloads")
        os.makedirs(folder, exist_ok=True)

        filename = f"{title}_{timestamp}.jpg"
        filepath = os.path.join(folder, filename)

        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(response.content)
            return send_file(filepath, as_attachment=True)
        return f"Failed to download image. Status code: {response.status_code}", 500
    except Exception as e:
        return f"Download failed: {str(e)}", 500

@app.route("/mongolian")
def top_mongolian():
    try:
        mongolian_movies = get_top_mongolian_movies(limit=20)
        return render_template("top_mongolian.html", movies=mongolian_movies)
    except Exception as e:
        return render_template("top_mongolian.html", movies=[], error=str(e))

if __name__ == "__main__":
    app.run(debug=True)
