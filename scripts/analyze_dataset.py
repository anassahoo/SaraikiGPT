import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    ROOT
    / "data"
    / "raw"
    / "news"
    / "app_saraiki"
    / "articles.jsonl"
)


def count_words(text):
    return len(text.split())


def count_saraiki_chars(text):
    # Arabic-script Unicode ranges
    chars = re.findall(r"[\u0600-\u06FF]", text)
    return len(chars)


def main():

    records = []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:

            line = line.strip()

            if not line:
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass


    total_articles = len(records)

    total_words = 0
    total_chars = 0
    total_arabic_chars = 0

    lengths = []

    titles = Counter()
    urls = Counter()


    for record in records:

        text = record.get("text", "")
        title = record.get("title", "")
        url = record.get("url", "")

        words = count_words(text)

        total_words += words
        total_chars += len(text)
        total_arabic_chars += count_saraiki_chars(text)

        lengths.append(words)

        titles[title] += 1
        urls[url] += 1


    duplicate_titles = sum(
        1 for count in titles.values()
        if count > 1
    )

    duplicate_urls = sum(
        1 for count in urls.values()
        if count > 1
    )


    average_words = (
        total_words / total_articles
        if total_articles
        else 0
    )

    min_words = min(lengths) if lengths else 0
    max_words = max(lengths) if lengths else 0


    arabic_ratio = (
        total_arabic_chars / total_chars * 100
        if total_chars
        else 0
    )


    print("=" * 60)
    print("APP SARAIKI DATASET ANALYSIS")
    print("=" * 60)

    print(f"Articles:          {total_articles:,}")
    print(f"Total words:       {total_words:,}")
    print(f"Total characters:  {total_chars:,}")

    print(
        f"Average words/article: "
        f"{average_words:,.2f}"
    )

    print(f"Shortest article:  {min_words:,} words")
    print(f"Longest article:   {max_words:,} words")

    print(f"Duplicate titles:  {duplicate_titles}")
    print(f"Duplicate URLs:    {duplicate_urls}")

    print(
        f"Arabic-script character ratio: "
        f"{arabic_ratio:.2f}%"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()