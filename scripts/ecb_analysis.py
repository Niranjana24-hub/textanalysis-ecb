import os
import re
import csv
from collections import Counter

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from wordcloud import WordCloud

# ── 1. CONFIGURATION ──────────────────────────────────────────────────────────
url = (
    "https://www.ecb.europa.eu/press/press_conference/"
    "monetary-policy-statement/2024/html/ecb.is241017~59ad385bab.en.html"
)

# ── 2. CREATE FOLDERS ─────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)

# ── 3. DOWNLOAD THE PAGE ──────────────────────────────────────────────────────
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; beginner-scraper/1.0)"
}

response = requests.get(url, headers=headers, timeout=10)

if response.status_code != 200:
    print("Error: failed to download the page.")
    raise SystemExit(1)

print("Downloaded page successfully")
print("Status code:", response.status_code)
print("Number of characters:", len(response.text))

# ── 4. PARSE THE PAGE ─────────────────────────────────────────────────────────
soup = BeautifulSoup(response.text, "html.parser")

main_section = soup.select_one("main div.section")
if main_section is None:
    print("Warning: main div.section not found.")
    main_section = soup

# ── 5. EXTRACT AND CLEAN PARAGRAPHS ───────────────────────────────────────────
paragraph_tags = main_section.select("p")

cleaned_paragraphs = []
for para in paragraph_tags:
    raw_text = para.get_text()
    cleaned_text = re.sub(r"\s+", " ", raw_text).strip()
    if len(cleaned_text) >= 30:
        cleaned_paragraphs.append(cleaned_text)

# ── 6. SAVE TEXT TO DATA FOLDER ───────────────────────────────────────────────
text_output_path = os.path.join("data", "ecb_press_conference_2024-10-17.txt")
with open(text_output_path, "w", encoding="utf-8") as text_file:
    for paragraph in cleaned_paragraphs:
        text_file.write(paragraph + "\n\n")

print(f"Saved {len(cleaned_paragraphs)} paragraphs to {text_output_path}")

# ── 7. SENTIMENT ANALYSIS WITH TEXTBLOB ───────────────────────────────────────
sentiment_rows = []
for index, paragraph in enumerate(cleaned_paragraphs, start=1):
    blob = TextBlob(paragraph)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.05:
        label = "Positive"
    elif polarity < -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    sentiment_rows.append({
        "paragraph_number": index,
        "paragraph_text": paragraph,
        "polarity": polarity,
        "subjectivity": subjectivity,
        "label": label,
    })

sentiment_output_path = os.path.join("output", "sentiment_by_paragraph.csv")
with open(sentiment_output_path, "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.DictWriter(
        csv_file,
        fieldnames=["paragraph_number", "paragraph_text",
                    "polarity", "subjectivity", "label"],
    )
    writer.writeheader()
    for row in sentiment_rows:
        writer.writerow(row)

print(f"Saved sentiment results to {sentiment_output_path}")

# ── 8. WORD FREQUENCY ─────────────────────────────────────────────────────────
common_stopwords = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any",
    "are", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for",
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself",
    "let", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "she", "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which",
    "while", "who", "whom", "why", "with", "would", "you", "your", "yours", "yourself",
    "yourselves",
}

ecb_specific_stopwords = {
    "ecb", "euro", "area", "per", "cent", "lagarde", "will", "us"
}

all_stopwords = common_stopwords.union(ecb_specific_stopwords)

word_counter = Counter()
for paragraph in cleaned_paragraphs:
    words = re.findall(r"\b[a-zA-Z']+\b", paragraph.lower())
    for word in words:
        if word not in all_stopwords and len(word) > 1:
            word_counter[word] += 1

most_common_words = word_counter.most_common(50)

# ── 9. SAVE TOP 50 WORDS TO CSV ───────────────────────────────────────────────
top_words_output_path = os.path.join("output", "ecb_top_words.csv")
with open(top_words_output_path, "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["word", "count"])
    for word, count in most_common_words:
        writer.writerow([word, count])

print(f"Saved top 50 words to {top_words_output_path}")

print("\nTop 10 words:")
for word, count in most_common_words[:10]:
    print(f"{word}: {count}")

# ── 10. GENERATE WORD CLOUD ───────────────────────────────────────────────────
filtered_text = " ".join(
    [word for word, _ in most_common_words
     for _ in range(word_counter[word])]
)

wordcloud = WordCloud(
    width=1200,
    height=800,
    background_color="white",
    collocations=False,
).generate(filtered_text)

wordcloud_output_path = os.path.join("output", "ecb_wordcloud.png")
wordcloud.to_file(wordcloud_output_path)
print(f"Saved word cloud to {wordcloud_output_path}")

# ── 11. WRITE SUMMARY ─────────────────────────────────────────────────────────
summary_text = (
    "ECB page used: https://www.ecb.europa.eu/press/press_conference/"
    "monetary-policy-statement/2024/html/ecb.is241017~59ad385bab.en.html\n\n"
    "TextBlob was chosen because it provides both polarity and subjectivity "
    "scores, works well with formal economic language, and is simple to apply "
    "paragraph by paragraph without any training data required. Unlike VADER "
    "which is designed for social media text, TextBlob handles formal "
    "institutional language more appropriately.\n\n"
    "Paragraph sentiment results show whether individual paragraphs are "
    "positive, negative, or neutral in tone. This helps identify the overall "
    "tone of the press conference and highlights which sections focus on "
    "economic conditions, policy decisions, or risks.\n"
)

summary_output_path = os.path.join("output", "summary.txt")
with open(summary_output_path, "w", encoding="utf-8") as summary_file:
    summary_file.write(summary_text)

print(f"Saved summary to {summary_output_path}") 