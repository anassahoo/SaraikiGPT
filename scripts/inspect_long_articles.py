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
# Configuration
# ============================================================

# Analyze articles above this length.
MIN_WORDS = 1500

# Number of repeated sentence/paragraph examples to display.
MAX_EXAMPLES = 20


# ============================================================
# Utilities
# ============================================================

def normalize_spaces(text):
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text):
    """
    Basic sentence splitter for Saraiki/Urdu Arabic-script text.
    This is heuristic and does not modify the original text.
    """
    sentences = re.split(
        r"(?<=[۔!?])\s+",
        text
    )

    return [
        normalize_spaces(sentence)
        for sentence in sentences
        if normalize_spaces(sentence)
    ]


def split_paragraphs(text):
    """
    Split text into paragraphs based on blank lines.
    """
    paragraphs = re.split(r"\n\s*\n", text)

    return [
        normalize_spaces(paragraph)
        for paragraph in paragraphs
        if normalize_spaces(paragraph)
    ]


def find_repeated_items(items):
    counter = Counter(items)

    return {
        item: count
        for item, count in counter.items()
        if count > 1
    }


# ============================================================
# Analyze article
# ============================================================

def analyze_article(article):

    title = str(
        article.get("title", "")
    ).strip()

    url = str(
        article.get("url", "")
    ).strip()

    article_id = article.get(
        "article_id",
        "N/A"
    )

    text = str(
        article.get("text", "")
    ).strip()

    words = text.split()

    print()
    print("=" * 80)
    print("LONG ARTICLE INSPECTION")
    print("=" * 80)

    print()
    print(f"Article ID: {article_id}")
    print(f"Title:      {title}")
    print(f"URL:        {url}")
    print(f"Words:      {len(words):,}")
    print(f"Characters: {len(text):,}")

    # --------------------------------------------------------
    # Paragraph analysis
    # --------------------------------------------------------

    paragraphs = split_paragraphs(text)

    print()
    print("-" * 80)
    print("PARAGRAPH ANALYSIS")
    print("-" * 80)

    print(
        f"Paragraphs detected: {len(paragraphs):,}"
    )

    paragraph_duplicates = find_repeated_items(
        paragraphs
    )

    print(
        f"Repeated paragraphs: {len(paragraph_duplicates):,}"
    )

    if paragraph_duplicates:

        print()
        print("Repeated paragraphs:")

        for paragraph, count in list(
            sorted(
                paragraph_duplicates.items(),
                key=lambda x: x[1],
                reverse=True
            )
        )[:MAX_EXAMPLES]:

            preview = paragraph

            if len(preview) > 300:
                preview = preview[:300] + "..."

            print()
            print(f"Occurrences: {count}")
            print(f"Text: {preview}")

    # --------------------------------------------------------
    # Sentence analysis
    # --------------------------------------------------------

    sentences = split_sentences(text)

    print()
    print("-" * 80)
    print("SENTENCE ANALYSIS")
    print("-" * 80)

    print(
        f"Sentences detected: {len(sentences):,}"
    )

    sentence_duplicates = find_repeated_items(
        sentences
    )

    print(
        f"Repeated sentences: {len(sentence_duplicates):,}"
    )

    if sentence_duplicates:

        print()
        print("Repeated sentences:")

        for sentence, count in list(
            sorted(
                sentence_duplicates.items(),
                key=lambda x: x[1],
                reverse=True
            )
        )[:MAX_EXAMPLES]:

            preview = sentence

            if len(preview) > 300:
                preview = preview[:300] + "..."

            print()
            print(f"Occurrences: {count}")
            print(f"Text: {preview}")

    # --------------------------------------------------------
    # Word frequency
    # --------------------------------------------------------

    print()
    print("-" * 80)
    print("WORD FREQUENCY")
    print("-" * 80)

    normalized_words = [
        word.strip(
            "،۔,!?;:\"'()[]{}"
        ).lower()
        for word in words
    ]

    normalized_words = [
        word
        for word in normalized_words
        if word
    ]

    word_counter = Counter(
        normalized_words
    )

    print(
        f"Unique words: {len(word_counter):,}"
    )

    print()
    print("Most frequent words:")

    for word, count in word_counter.most_common(30):

        print(
            f"{count:>6}  {word}"
        )

    # --------------------------------------------------------
    # Beginning and ending
    # --------------------------------------------------------

    print()
    print("-" * 80)
    print("ARTICLE BEGINNING")
    print("-" * 80)

    beginning = normalize_spaces(text[:1500])

    print(beginning)

    print()
    print("-" * 80)
    print("ARTICLE END")
    print("-" * 80)

    ending = normalize_spaces(text[-1500:])

    print(ending)


# ============================================================
# Main
# ============================================================

def main():

    if not INPUT_FILE.exists():

        print("ERROR: Dataset file not found:")
        print(INPUT_FILE)

        return

    print("=" * 80)
    print("APP SARAIKI LONG ARTICLE INSPECTOR")
    print("=" * 80)

    articles = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        for line_number, line in enumerate(
            f,
            start=1
        ):

            line = line.strip()

            if not line:
                continue

            try:

                article = json.loads(line)

                articles.append(article)

            except json.JSONDecodeError:

                print(
                    f"WARNING: Invalid JSON at line {line_number}"
                )

    # --------------------------------------------------------
    # Find long articles
    # --------------------------------------------------------

    long_articles = []

    for article in articles:

        text = str(
            article.get("text", "")
        ).strip()

        words = len(text.split())

        if words >= MIN_WORDS:

            long_articles.append(
                (words, article)
            )

    long_articles.sort(
        key=lambda x: x[0],
        reverse=True
    )

    print()
    print(
        f"Articles with >= {MIN_WORDS:,} words: "
        f"{len(long_articles):,}"
    )

    # --------------------------------------------------------
    # Inspect each long article
    # --------------------------------------------------------

    for words, article in long_articles:

        analyze_article(article)

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("INSPECTION COMPLETE")
    print("=" * 80)

    print()
    print("The raw dataset was NOT modified.")
    print(f"Input: {INPUT_FILE}")


if __name__ == "__main__":
    main()