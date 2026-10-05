import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT
    / "data"
    / "extracted"
    / "app_saraiki_clean.jsonl"
)


def count_words(text):
    return len(text.split())


def normalize_for_duplicate(text):
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text):
    return [
        s.strip()
        for s in re.split(r"(?<=[۔.!؟])\s+", text)
        if s.strip()
    ]


def split_paragraphs(text):
    return [
        p.strip()
        for p in text.split("\n\n")
        if p.strip()
    ]


def main():

    print("Loading cleaned APP dataset...")
    print("Input:", INPUT_FILE)

    articles = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                articles.append(json.loads(line))
            except json.JSONDecodeError:
                print("WARNING: Invalid JSON skipped.")

    print("Articles loaded:", f"{len(articles):,}")

    # ========================================================
    # Basic statistics
    # ========================================================

    word_counts = []
    char_counts = []

    duplicate_texts = Counter()
    duplicate_titles = Counter()

    empty_articles = []
    short_articles = []
    long_articles = []

    total_arabic = 0
    total_saraiki_specific = 0
    total_latin = 0
    total_digits = 0
    total_chars = 0

    saraiki_chars = set("ݙ ڑ ں ݨ ݩ ݱ ݭ ݜ ݬ".replace(" ", ""))

    # ========================================================
    # Repetition statistics
    # ========================================================

    articles_with_repeated_sentences = []
    articles_with_repeated_paragraphs = []

    # ========================================================
    # Analyze each article
    # ========================================================

    for article in articles:

        text = str(article.get("text", "")).strip()
        title = str(article.get("title", "")).strip()

        if not text:
            empty_articles.append(article)
            continue

        words = count_words(text)
        chars = len(text)

        word_counts.append(words)
        char_counts.append(chars)

        duplicate_texts[normalize_for_duplicate(text)] += 1

        if title:
            duplicate_titles[title] += 1

        if words < 50:
            short_articles.append(article)

        if words >= 1500:
            long_articles.append(article)

        # ----------------------------------------------------
        # Character statistics
        # ----------------------------------------------------

        for char in text:

            total_chars += 1

            code = ord(char)

            if (
                0x0600 <= code <= 0x06FF
                or 0x0750 <= code <= 0x077F
                or 0x08A0 <= code <= 0x08FF
            ):
                total_arabic += 1

            if char in saraiki_chars:
                total_saraiki_specific += 1

            if char.isascii() and char.isalpha():
                total_latin += 1

            if char.isdigit():
                total_digits += 1

        # ----------------------------------------------------
        # Repeated sentences
        # ----------------------------------------------------

        sentences = split_sentences(text)

        sentence_counts = Counter(sentences)

        repeated_sentences = [
            sentence
            for sentence, count in sentence_counts.items()
            if count > 1
        ]

        if repeated_sentences:
            articles_with_repeated_sentences.append(
                {
                    "title": title,
                    "url": article.get("url", ""),
                    "word_count": words,
                    "repeated_sentences": repeated_sentences,
                }
            )

        # ----------------------------------------------------
        # Repeated paragraphs
        # ----------------------------------------------------

        paragraphs = split_paragraphs(text)

        paragraph_counts = Counter(paragraphs)

        repeated_paragraphs = [
            paragraph
            for paragraph, count in paragraph_counts.items()
            if count > 1
        ]

        if repeated_paragraphs:
            articles_with_repeated_paragraphs.append(
                {
                    "title": title,
                    "url": article.get("url", ""),
                    "word_count": words,
                    "repeated_paragraphs": repeated_paragraphs,
                }
            )

    # ========================================================
    # Duplicate information
    # ========================================================

    exact_duplicate_groups = {
        text: count
        for text, count in duplicate_texts.items()
        if count > 1
    }

    duplicate_title_groups = {
        title: count
        for title, count in duplicate_titles.items()
        if count > 1
    }

    # ========================================================
    # Sort longest articles
    # ========================================================

    long_articles.sort(
        key=lambda x: count_words(str(x.get("text", ""))),
        reverse=True
    )

    # ========================================================
    # Print report
    # ========================================================

    print()
    print("=" * 70)
    print("APP CLEANED CORPUS VALIDATION")
    print("=" * 70)

    print()
    print("BASIC STATISTICS")
    print("-" * 70)

    print(f"Articles:                 {len(articles):,}")
    print(f"Total words:              {sum(word_counts):,}")
    print(f"Total characters:         {sum(char_counts):,}")

    if word_counts:
        print(f"Average words/article:    {sum(word_counts) / len(word_counts):.2f}")
        print(f"Shortest article:         {min(word_counts):,} words")
        print(f"Longest article:          {max(word_counts):,} words")

    print()
    print("DUPLICATES")
    print("-" * 70)

    print(f"Exact duplicate text groups: {len(exact_duplicate_groups):,}")
    print(f"Duplicate title groups:      {len(duplicate_title_groups):,}")

    print()
    print("REPETITION")
    print("-" * 70)

    print(
        f"Articles with repeated sentences: "
        f"{len(articles_with_repeated_sentences):,}"
    )

    print(
        f"Articles with repeated paragraphs: "
        f"{len(articles_with_repeated_paragraphs):,}"
    )

    print()
    print("ARTICLE LENGTH")
    print("-" * 70)

    print(f"Articles < 50 words:      {len(short_articles):,}")
    print(f"Articles >= 1500 words:   {len(long_articles):,}")

    print()
    print("CHARACTER DISTRIBUTION")
    print("-" * 70)

    if total_chars:

        print(
            f"Arabic-derived script:    "
            f"{total_arabic / total_chars * 100:.2f}%"
        )

        print(
            f"Saraiki-specific chars:   "
            f"{total_saraiki_specific / total_chars * 100:.4f}%"
        )

        print(
            f"Latin letters:            "
            f"{total_latin / total_chars * 100:.2f}%"
        )

        print(
            f"Digits:                   "
            f"{total_digits / total_chars * 100:.2f}%"
        )

    # ========================================================
    # Longest articles
    # ========================================================

    print()
    print("TOP 15 LONGEST ARTICLES")
    print("-" * 70)

    for i, article in enumerate(long_articles[:15], 1):

        title = str(article.get("title", "")).strip()
        words = count_words(str(article.get("text", "")))
        url = article.get("url", "")

        print()
        print(f"{i}. {words:,} words")
        print(f"Title: {title}")
        print(f"URL:   {url}")

    # ========================================================
    # Repeated sentence examples
    # ========================================================

    if articles_with_repeated_sentences:

        print()
        print("REPEATED SENTENCE EXAMPLES")
        print("-" * 70)

        for article in articles_with_repeated_sentences[:10]:

            print()
            print("Title:", article["title"])
            print("URL:", article["url"])

            for sentence in article["repeated_sentences"][:3]:

                print("  >", sentence[:300])

    # ========================================================
    # Repeated paragraph examples
    # ========================================================

    if articles_with_repeated_paragraphs:

        print()
        print("REPEATED PARAGRAPH EXAMPLES")
        print("-" * 70)

        for article in articles_with_repeated_paragraphs[:10]:

            print()
            print("Title:", article["title"])
            print("URL:", article["url"])

            for paragraph in article["repeated_paragraphs"][:2]:

                print("  >", paragraph[:300])

    # ========================================================
    # Short article examples
    # ========================================================

    print()
    print("SHORT ARTICLE EXAMPLES")
    print("-" * 70)

    for article in short_articles[:10]:

        text = str(article.get("text", ""))

        print()
        print(
            f"{count_words(text)} words | "
            f"{article.get('title', '')}"
        )

        print(text[:250].replace("\n", " "))

    print()
    print("=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()