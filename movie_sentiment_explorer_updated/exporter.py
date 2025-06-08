# exporter.py
from fpdf import FPDF
import csv


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

