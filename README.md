## Overview
This project scrapes, cleans, and analyses the ECB Monetary Policy
Press Conference from 17 October 2024. It performs paragraph-level
sentiment analysis using TextBlob and generates a word cloud to
identify the key themes discussed in the press conference.
## Target Page
https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/2024/html/ecb.is241017~59ad385bab.en.html 

## Packages Used
| Package | Purpose |
|---|---|
| `requests` | Downloads the ECB web page |
| `beautifulsoup4` | Parses the HTML content |
| `textblob` | Paragraph-level sentiment analysis |
| `wordcloud` | Generates the word cloud image |
| `csv` | Writes output CSV files (built-in Python module) |
| `os` | Creates folders and manages file paths (built-in) |
| `re` | Cleans text with regular expressions (built-in) |
| `collections` | Counts word frequencies (built-in) |

Open the VS Code terminal: 
conda --version 
ouput conda 25.7.0
## Step 1 — Set Up the Environment 

#### Copilot Prompt 
```
I am a beginner using a Mac with VS Code. Help me set up a conda
environment for a Python textual analysis project. I need requests,
beautifulsoup4, textblob and wordcloud. Explain each command slowly
and tell me how to verify that the environment is active.
```
### 1.1 Create environment.yml
**In VS Code:**
Create a new file in the root of the project and name it
`environment.yml` 
name: textanalysis
channels:
  - conda-forge
dependencies:
  - python=3.11
  - requests
  - beautifulsoup4
  - textblob
  - wordcloud

Save with **Cmd+S**


### 1.2 Create and Activate the Environment
**Mac — VS Code Terminal:**
Open terminal in VS Code with **Ctrl+`** (backtick)

Make sure you are in the project folder:
```
cd ~/Desktop/textanalysis-ecb
```

Create the environment — run this once only:
```
conda env create -f environment.yml
```

Wait until it finishes. Then activate it:
```
conda activate textanalysis
```

You should see **(textanalysis)** at the start of the line.
### 1.3 Create Scripts Folder
**Mac — VS Code Terminal:**
```
mkdir scripts
```

## Step 2 — Download the Web Page
#### Copilot Prompt 
```
Write beginner-friendly Python code using requests to download
this ECB page:
https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/2024/html/ecb.is241017~59ad385bab.en.html
Use a User-Agent header and a timeout. Print the status code and
length of the HTML. Explain every line.
```
### 2.1 Create the Script File
**In VS Code:**
Create a new file inside the `scripts/` folder and name it `ecb_analysis.py`
### 2.2 Start with this code:
```python
import os
import requests
# Step 1: Define the ECB page URL
url = (
    "https://www.ecb.europa.eu/press/press_conference/"
    "monetary-policy-statement/2024/html/ecb.is241017~59ad385bab.en.html"
)

# Step 2: Create folders automatically if they do not exist
os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)

# Step 3: Set browser-like headers
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; beginner-scraper/1.0)"
}
# Step 4: Download the page
response = requests.get(url, headers=headers, timeout=10)

# Step 5: Check it worked
if response.status_code != 200:
    print("Error: failed to download the page.")
    raise SystemExit(1)

print("Downloaded page successfully")
print("Status code:", response.status_code)
print("Number of characters:", len(response.text))
```
### 2.3 Run it
**Mac — VS Code Terminal**
(make sure **(textanalysis)** is active and you are in `textanalysis-ecb` folder):
```
python3 scripts/ecb_analysis.py
```

Expected result:
```
Downloaded page successfully
Status code: 200
Number of characters: many thousands
``` 

## Step 3 — Parse the Page and Extract Text
#### Copilot Prompt 
```
Help me parse the ECB page with BeautifulSoup. The useful article
text is inside the CSS selector main div.section. Extract all
paragraph tags, clean the whitespace, skip paragraphs shorter
than 30 characters, and save the result as a plain text file.
Write beginner-friendly code and explain each block.
```
### 3.1 Replace your script with this version:
```python
import os
import re
import requests
from bs4 import BeautifulSoup

url = (
    "https://www.ecb.europa.eu/press/press_conference/"
    "monetary-policy-statement/2024/html/ecb.is241017~59ad385bab.en.html"
)

os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; beginner-scraper/1.0)"
}

response = requests.get(url, headers=headers, timeout=10)

if response.status_code != 200:
    print("Error: failed to download the page.")
    raise SystemExit(1)
# Step 1: Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# Step 2: Find the main article section
main_section = soup.select_one("main div.section")
if main_section is None:
    print("Warning: main div.section not found.")
    main_section = soup

# Step 3: Extract all paragraph tags
paragraph_tags = main_section.select("p")

# Step 4: Clean and filter paragraphs
cleaned_paragraphs = []
for para in paragraph_tags:
    raw_text = para.get_text()
    cleaned_text = re.sub(r"\s+", " ", raw_text).strip()
    if len(cleaned_text) >= 30:
        cleaned_paragraphs.append(cleaned_text)

# Step 5: Save to data folder
text_output_path = os.path.join("data", "ecb_press_conference_2024-10-17.txt")
with open(text_output_path, "w", encoding="utf-8") as text_file:
    for paragraph in cleaned_paragraphs:
        text_file.write(paragraph + "\n\n")

print(f"Saved {len(cleaned_paragraphs)} paragraphs to {text_output_path}")
```
### 3.2 Run it
**Mac — VS Code Terminal:**
```
python3 scripts/ecb_analysis.py
```

Expected result:
```
Saved X paragraphs to data/ecb_press_conference_2024-10-17.txt
```

## Step 4 — Sentiment Analysis with TextBlob
#### Copilot Prompt for This Step
```
Add paragraph-level sentiment analysis to my ECB text scraping
script. Use TextBlob instead of VADER. For each paragraph score
the polarity and subjectivity, add a simple Positive/Neutral/
Negative label, save the result as output/sentiment_by_paragraph.csv
and explain the limitations for central bank text.
```
### 4.1 Add this to your script:
```python
import csv
from textblob import TextBlob

# Step 1: Analyse sentiment for each paragraph
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
# Step 2: Save sentiment results to CSV
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
```
### 4.2 Run it
**Mac — VS Code Terminal:**
```
python3 scripts/ecb_analysis.py
```

Expected result:
```
Saved X paragraphs to data/ecb_press_conference_2024-10-17.txt
Saved sentiment results to output/sentiment_by_paragraph.csv
```

How to read the result — open `output/sentiment_by_paragraph.csv`:

| Column | Meaning |
|---|---|
| `paragraph_number` | Order of the paragraph |
| `paragraph_text` | Full paragraph text |
| `polarity` | Score from -1 (negative) to +1 (positive) |
| `subjectivity` | Score from 0 (objective) to 1 (subjective) |
| `label` | Positive, Negative or Neutral |
## Step 5 — Word Frequency and Word Cloud 
#### Copilot Prompt for This Step
```
Add a word frequency analysis and word cloud to my ECB text
analysis script. Use the wordcloud package. Remove common English
stopwords and ECB specific words like ecb, euro, area, per, cent
and lagarde. Save output/ecb_top_words.csv and
output/ecb_wordcloud.png. Print the top 10 words. Also write a
short summary to output/summary.txt explaining which ECB page was
used, why TextBlob was chosen, and what the results suggest.
Explain how stopwords affect the result.
```
### 5.1 Add this to your script:
```python
from collections import Counter
from wordcloud import WordCloud

# Step 1: Define stop words
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
    "yourselves", "us"
}

ecb_specific_stopwords = {
    "ecb", "euro", "area", "per", "cent", "lagarde", "will"
}

all_stopwords = common_stopwords.union(ecb_specific_stopwords)

# Step 2: Count words
word_counter = Counter()
for paragraph in cleaned_paragraphs:
    words = re.findall(r"\b[a-zA-Z']+\b", paragraph.lower())
    for word in words:
        if word not in all_stopwords and len(word) > 1:
            word_counter[word] += 1

most_common_words = word_counter.most_common(50)

# Step 3: Save top 50 words to CSV
top_words_output_path = os.path.join("output", "ecb_top_words.csv")
with open(top_words_output_path, "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["word", "count"])
    for word, count in most_common_words:
        writer.writerow([word, count])

print(f"Saved top 50 words to {top_words_output_path}")

# Step 4: Print top 10 words
print("\nTop 10 words:")
for word, count in most_common_words[:10]:
    print(f"{word}: {count}")

# Step 5: Generate word cloud
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

# Step 6: Write summary
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
```

### 5.2 Run the final complete script
**Mac — VS Code Terminal**
(make sure **(textanalysis)** is active and you are in `textanalysis-ecb` folder):
```
python3 scripts/ecb_analysis.py
```

Expected result:
```
Saved X paragraphs to data/ecb_press_conference_2024-10-17.txt
Saved sentiment results to output/sentiment_by_paragraph.csv
Saved top 50 words to output/ecb_top_words.csv
Top 10 words:
...
Saved word cloud to output/ecb_wordcloud.png
Saved summary to output/summary.txt
``` 