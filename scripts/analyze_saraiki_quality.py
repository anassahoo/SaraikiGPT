import json
import re
from pathlib import Path
from collections import Counter


# ============================================================
# Paths
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "news"
    / "app_saraiki"
    / "articles.jsonl"
)


# ============================================================
# Saraiki / Arabic-script characters
# ============================================================

# Characters commonly found in Saraiki writing.
# This is a heuristic, not a language classifier.
SARAIKI_CHARS = set(
    "ٻڄڃچڌڏڊڎڑژکگںھ"
)


# Arabic-derived script range
ARABIC_RANGE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")


# Latin characters
LATIN_RANGE = re.compile(r"[A-Za-z]")


# Digits
DIGIT_RANGE = re.compile(r"\d")


# ============================================================
# Text utilities
# ============================================================

def normalize_spaces(text):
    """Normalize repeated whitespace."""
    return re.sub(r"\s+", " ", text).strip()


def count_words(text):
    """Count whitespace-separated words."""
    return len(text.split())


def arabic_character_ratio(text):
    """Percentage of characters belonging to Arabic-derived Unicode blocks."""
    if not text:
        return 0.0

    arabic_chars = len(ARABIC_RANGE.findall(text))

    # Ignore whitespace when calculating the ratio.
    meaningful_chars = len(re.sub(r"\s", "", text))

    if meaningful_chars == 0:
        return 0.0

    return (arabic_chars / meaningful_chars) * 100


def saraiki_character_count(text):
    """Count occurrences of characters commonly associated with Saraiki."""
    return sum(1 for char in text if char in SARAIKI_CHARS)


def saraiki_character_ratio(text):
    """
    Percentage of meaningful characters that are Saraiki-specific
    characters from our heuristic character set.
    """
    if not text:
        return 0.0

    meaningful_chars = len(re.sub(r"\s", "", text))

    if meaningful_chars == 0:
        return 0.0

    return (saraiki_character_count(text) / meaningful_chars) * 100


def latin_character_ratio(text):
    """Percentage of Latin alphabet characters."""
    if not text:
        return 0.0

    latin_chars = len(LATIN_RANGE.findall(text))
    meaningful_chars = len(re.sub(r"\s", "", text))

    if meaningful_chars == 0:
        return 0.0

    return (latin_chars / meaningful_chars) * 100


def digit_ratio(text):
    """Percentage of digits among meaningful characters."""
    if not text:
        return 0.0

    digits = len(DIGIT_RANGE.findall(text))
    meaningful_chars = len(re.sub(r"\s", "", text))

    if meaningful_chars == 0:
        return 0.0

    return (digits / meaningful_chars) * 100


# ============================================================
# Main analysis
# ============================================================

def main():

    if not INPUT_FILE.exists():
        print("ERROR: Dataset file not found:")
        print(INPUT_FILE)
        return

    print("=" * 70)
    print("SARAIKI CORPUS QUALITY ANALYSIS")
    print("=" * 70)

    articles = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:

        for line_number, line in enumerate(f, start=1):

            line = line.strip()

            if not line:
                continue

            try:
                article = json.loads(line)
                articles.append(article)

            except json.JSONDecodeError:
                print(
                    f"WARNING: Invalid JSON on line {line_number}"
                )

    print()
    print(f"Articles loaded: {len(articles):,}")

    # --------------------------------------------------------
    # Overall statistics
    # --------------------------------------------------------

    total_words = 0
    total_chars = 0

    word_lengths = []

    saraiki_char_total = 0
    arabic_char_total = 0
    latin_char_total = 0
    digit_char_total = 0

    short_articles = []
    long_articles = []

    empty_articles = []

    titles = []
    urls = []

    # --------------------------------------------------------
    # Analyze each article
    # --------------------------------------------------------

    for article in articles:

        title = str(article.get("title", "")).strip()
        text = str(article.get("text", "")).strip()
        url = str(article.get("url", "")).strip()

        titles.append(title)
        urls.append(url)

        words = count_words(text)

        total_words += words
        total_chars += len(text)

        if words > 0:
            word_lengths.append(words)

        # Character analysis
        saraiki_char_total += saraiki_character_count(text)

        arabic_char_total += len(
            ARABIC_RANGE.findall(text)
        )

        latin_char_total += len(
            LATIN_RANGE.findall(text)
        )

        digit_char_total += len(
            DIGIT_RANGE.findall(text)
        )

        # Very short articles
        if 0 < words < 50:
            short_articles.append(
                (words, title, url)
            )

        # Very long articles
        if words > 3000:
            long_articles.append(
                (words, title, url)
            )

        if words == 0:
            empty_articles.append(
                (title, url)
            )

    # --------------------------------------------------------
    # Duplicate titles
    # --------------------------------------------------------

    title_counter = Counter(
        title.lower()
        for title in titles
        if title
    )

    duplicate_titles = {
        title: count
        for title, count in title_counter.items()
        if count > 1
    }

    # --------------------------------------------------------
    # Duplicate URLs
    # --------------------------------------------------------

    url_counter = Counter(
        url
        for url in urls
        if url
    )

    duplicate_urls = {
        url: count
        for url, count in url_counter.items()
        if count > 1
    }

    # --------------------------------------------------------
    # Overall ratios
    # --------------------------------------------------------

    if total_chars > 0:

        arabic_ratio = (
            arabic_char_total / total_chars
        ) * 100

        saraiki_ratio = (
            saraiki_char_total / total_chars
        ) * 100

        latin_ratio = (
            latin_char_total / total_chars
        ) * 100

        digit_ratio_value = (
            digit_char_total / total_chars
        ) * 100

    else:
        arabic_ratio = 0
        saraiki_ratio = 0
        latin_ratio = 0
        digit_ratio_value = 0

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("CORPUS SIZE")
    print("-" * 70)

    print(f"Articles:              {len(articles):,}")
    print(f"Total words:           {total_words:,}")
    print(f"Total characters:      {total_chars:,}")

    if word_lengths:
        average_words = total_words / len(articles)

        print(
            f"Average words/article: {average_words:,.2f}"
        )

        print(
            f"Shortest article:      {min(word_lengths):,} words"
        )

        print(
            f"Longest article:       {max(word_lengths):,} words"
        )

    print()
    print("-" * 70)
    print("LANGUAGE / CHARACTER ANALYSIS")
    print("-" * 70)

    print(
        f"Arabic-script ratio:   {arabic_ratio:.2f}%"
    )

    print(
        f"Saraiki-specific chars:{saraiki_ratio:.4f}%"
    )

    print(
        f"Latin character ratio: {latin_ratio:.2f}%"
    )

    print(
        f"Digit ratio:           {digit_ratio_value:.2f}%"
    )

    print()
    print("-" * 70)
    print("DUPLICATES")
    print("-" * 70)

    print(
        f"Duplicate titles:      {len(duplicate_titles):,}"
    )

    print(
        f"Duplicate URLs:        {len(duplicate_urls):,}"
    )

    print()
    print("-" * 70)
    print("ARTICLE QUALITY FLAGS")
    print("-" * 70)

    print(
        f"Empty articles:        {len(empty_articles):,}"
    )

    print(
        f"Articles < 50 words:   {len(short_articles):,}"
    )

    print(
        f"Articles > 3000 words: {len(long_articles):,}"
    )

    # --------------------------------------------------------
    # Duplicate titles
    # --------------------------------------------------------

    if duplicate_titles:

        print()
        print("-" * 70)
        print("DUPLICATE TITLES")
        print("-" * 70)

        for title, count in sorted(
            duplicate_titles.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]:

            print(
                f"{count}x  {title}"
            )

    # --------------------------------------------------------
    # Very short articles
    # --------------------------------------------------------

    if short_articles:

        print()
        print("-" * 70)
        print("SAMPLE SHORT ARTICLES")
        print("-" * 70)

        for words, title, url in short_articles[:20]:

            print()
            print(f"Words: {words}")
            print(f"Title: {title}")
            print(f"URL:   {url}")

    # --------------------------------------------------------
    # Very long articles
    # --------------------------------------------------------

    if long_articles:

        print()
        print("-" * 70)
        print("SAMPLE LONG ARTICLES")
        print("-" * 70)

        for words, title, url in sorted(
            long_articles,
            reverse=True
        )[:20]:

            print()
            print(f"Words: {words}")
            print(f"Title: {title}")
            print(f"URL:   {url}")

    # --------------------------------------------------------
    # Final interpretation
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    print()
    print("Important:")
    print(
        "The Saraiki-specific character ratio is only a heuristic."
    )

    print(
        "It should NOT be treated as a definitive Saraiki language classifier."
    )

    print()
    print("Raw dataset was NOT modified.")
    print(f"Input: {INPUT_FILE}")


if __name__ == "__main__":
    main()