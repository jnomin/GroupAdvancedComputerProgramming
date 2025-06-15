# exporter.py
from fpdf import FPDF
import csv
import os


def save_as_pdf(filename, title, metadata, plot, sentiment, reviews):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(0, 10, title, ln=True)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, metadata + "\n\n" + plot + f"\n\nAvg Sentiment: {sentiment:.3f}\n")

    pdf.set_font("Arial", 'B', size=13)
    pdf.cell(0, 10, "Reviews + Sentiment", ln=True)

    pdf.set_font("Arial", size=11)
    for i, (text, label) in enumerate(reviews, 1):
        clean_label = label.encode('ascii', 'ignore').decode()
        clean_text = text.encode('ascii', 'ignore').decode()
        pdf.multi_cell(0, 8, f"{i}. [{clean_label}] {clean_text[:200]}...")

    pdf.output(filename)


def save_as_csv(filename, reviews):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Review", "Sentiment Label"])
        for text, label in reviews:
            writer.writerow([text, label])


def save_chart_pdf(filename, movie, sentiment_counts, chart_path):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"{movie.title} ({movie.year})", ln=True)
    pdf.cell(200, 10, txt=f"Genre: {movie.genre}", ln=True)
    pdf.cell(200, 10, txt=f"Director: {movie.director}", ln=True)
    pdf.cell(200, 10, txt=f"IMDb Rating: {movie.imdb_rating}/10", ln=True)
    pdf.ln(10)
    pdf.image(chart_path, x=30, y=None, w=150)
    pdf.output(filename)


def save_pie_chart(chart_path, sentiment_counts):
    import matplotlib.pyplot as plt

    labels = sentiment_counts.keys()
    values = sentiment_counts.values()
    colors = ['#4caf50', '#ffc107', '#f44336']

    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.figure(figsize=(4, 4))
    plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors)
    plt.title("Sentiment Distribution")
    plt.savefig(chart_path)
    plt.close()
