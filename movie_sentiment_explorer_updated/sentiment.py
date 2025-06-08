# sentiment.py
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyze_sentiment(text: str) -> dict:
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(text)

# Optional test
if __name__ == "__main__":
    review = "This movie was amazing! I loved the visuals and story."
    print(analyze_sentiment(review))
