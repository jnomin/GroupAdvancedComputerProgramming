from flask import Flask, render_template, request, send_file
from api_handler import fetch_movie_data
from scraper import get_imdb_reviews
from sentiment import analyze_sentiment
from exporter import save_as_pdf, save_as_csv
import os
import requests
from urllib.parse import unquote

app = Flask(__name__)

def summarize_sentiment(reviews):
    scores = [analyze_sentiment(r)['compound'] for r in reviews]
    avg_score = round(sum(scores) / len(scores), 3)
    return avg_score

def sentiment_label(score):
    if score >= 0.5:
        return "Positive 😊"
    elif score <= -0.3:
        return "Negative 😠"
    else:
        return "Neutral 😐"

@app.route("/", methods=["GET", "POST"])
def index():
    movie = None
    reviews = []
    sentiment = None
    error = None

    if request.method == "POST":
        title = request.form["title"]
        try:
            movie = fetch_movie_data(title)
            reviews_raw = get_imdb_reviews(title)
            if not reviews_raw:
                raise Exception("No reviews found.")
            sentiment = summarize_sentiment(reviews_raw)
            reviews = [(r, sentiment_label(analyze_sentiment(r)["compound"])) for r in reviews_raw]
        except Exception as e:
            error = str(e)

    return render_template("index.html", movie=movie, reviews=reviews, sentiment=sentiment, error=error)

@app.route("/export/pdf")
def export_pdf():
    title = request.args.get("title")
    if not title:
        return "Missing title"
    try:
        movie = fetch_movie_data(title)
        reviews_raw = get_imdb_reviews(title)
        sentiment = summarize_sentiment(reviews_raw)
        reviews = [(r, sentiment_label(analyze_sentiment(r)["compound"])) for r in reviews_raw]
        save_as_pdf("movie_report.pdf", movie.title, f"Year: {movie.year}\nRating: {movie.imdb_rating}", movie.plot, sentiment, reviews)
        return send_file("movie_report.pdf", as_attachment=True)
    except:
        return "Failed to export PDF."

@app.route("/export/csv")
def export_csv():
    title = request.args.get("title")
    if not title:
        return "Missing title"
    try:
        reviews_raw = get_imdb_reviews(title)
        reviews = [(r, sentiment_label(analyze_sentiment(r)["compound"])) for r in reviews_raw]
        save_as_csv("movie_reviews.csv", reviews)
        return send_file("movie_reviews.csv", as_attachment=True)
    except:
        return "Failed to export CSV."

@app.route("/download-poster")
def download_poster():
    poster_url = request.args.get("url")
    if not poster_url:
        return "Missing poster URL"

    try:
        poster_url = unquote(poster_url)
        filename = "poster.jpg"
        response = requests.get(poster_url, timeout=10)
        with open(filename, "wb") as f:
            f.write(response.content)
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Download failed: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/download-poster")
def download_poster():
    poster_url = request.args.get("url")
    if not poster_url:
        return "Missing poster URL", 400

    try:
        filename = "poster.jpg"
        response = requests.get(poster_url, timeout=10)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            return send_file(filename, as_attachment=True)
        else:
            return f"Failed to download image. Status code: {response.status_code}", 500
    except Exception as e:
        return f"Download failed: {str(e)}", 500
