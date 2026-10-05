import json
import re
from pathlib import Path


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

OUTPUT_JSONL = (
    ROOT
    / "data"
    / "extracted"
    / "app_saraiki_clean.jsonl"
)

OUTPUT_TXT = (
    ROOT
    / "data"
    / "extracted"
    / "app_saraiki_clean.txt"
)


# ============================================================
# Text normalization
# ============================================================

def normalize_text(text):
    """
    Conservative text normalization.

    We do NOT rewrite Saraiki words.
    We only clean obvious formatting problems.
    """

    if not text:
        return ""

    text = str(text)

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove spaces at beginning/end of lines
    lines = [line.strip() for line in text.split("\n")]

    # Remove empty lines at beginning/end
    while lines and not lines[0]:
        lines.pop(0)

    while lines and not lines[-1]:
        lines.pop()

    text = "\n".join(lines)

    return text.strip()


# ============================================================
# Detect archive/category pages
# ============================================================

def is_archive_page(article):
    """
    APP archive/category pages were accidentally collected
    as article records.

    Example:
        /national/page/10/

    These are not individual news articles.
    """

    url = str(article.get("url", "")).lower()

    archive_patterns = [
        "/national/page/",
        "/page/",
    ]

    for pattern in archive_patterns:
        if pattern in url:
            return True

    return False


# ============================================================
# Remove exact repeated sentences
# ============================================================

def remove_repeated_sentences(text):
    """
    Remove consecutive identical sentences.

    This is intentionally conservative.
    Only exact repetitions are removed.
    """

    # Split while keeping punctuation
    sentences = re.split(
        r"(?<=[۔.!؟])\s+",
        text
    )

    cleaned = []
    previous = None

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        normalized = re.sub(r"\s+", " ", sentence)

        if normalized == previous:
            continue

        cleaned.append(sentence)
        previous = normalized

    return " ".join(cleaned)


# ============================================================
# Remove consecutive duplicate paragraphs
# ============================================================

def remove_repeated_paragraphs(text):
    """
    Remove consecutive identical paragraphs.
    """

    paragraphs = text.split("\n\n")

    cleaned = []
    previous = None

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        normalized = re.sub(r"\s+", " ", paragraph)

        if normalized == previous:
            continue

        cleaned.append(paragraph)
        previous = normalized

    return "\n\n".join(cleaned)


# ============================================================
# Main cleaning pipeline
# ============================================================

def main():

    print("Loading APP dataset...")
    print("Input:", INPUT_FILE)

    articles = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            try:
                article = json.loads(line)
                articles.append(article)

            except json.JSONDecodeError:
                print("Warning: invalid JSON line skipped.")

    print("Raw records loaded:", len(articles))

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    archive_removed = 0
    empty_removed = 0
    duplicate_removed = 0

    seen_texts = set()

    cleaned_articles = []

    # --------------------------------------------------------
    # Process articles
    # --------------------------------------------------------

    for article in articles:

        # ----------------------------------------------------
        # Remove archive/category pages
        # ----------------------------------------------------

        if is_archive_page(article):

            archive_removed += 1
            continue

        # ----------------------------------------------------
        # Get article text
        # ----------------------------------------------------

        text = article.get("text", "")

        text = normalize_text(text)

        if not text:

            empty_removed += 1
            continue

        # ----------------------------------------------------
        # Remove exact repeated paragraphs
        # ----------------------------------------------------

        text = remove_repeated_paragraphs(text)

        # ----------------------------------------------------
        # Remove exact repeated sentences
        # ----------------------------------------------------

        text = remove_repeated_sentences(text)

        # ----------------------------------------------------
        # Normalize again
        # ----------------------------------------------------

        text = normalize_text(text)

        if not text:

            empty_removed += 1
            continue

        # ----------------------------------------------------
        # Exact article deduplication
        # ----------------------------------------------------

        normalized_for_hash = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        if normalized_for_hash in seen_texts:

            duplicate_removed += 1
            continue

        seen_texts.add(normalized_for_hash)

        # ----------------------------------------------------
        # Create cleaned record
        # ----------------------------------------------------

        cleaned_article = dict(article)

        cleaned_article["text"] = text

        cleaned_articles.append(cleaned_article)

    # ========================================================
    # Save cleaned JSONL
    # ========================================================

    OUTPUT_JSONL.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_JSONL,
        "w",
        encoding="utf-8"
    ) as f:

        for article in cleaned_articles:

            f.write(
                json.dumps(
                    article,
                    ensure_ascii=False
                )
                + "\n"
            )

    # ========================================================
    # Save plain text corpus
    # ========================================================

    with open(
        OUTPUT_TXT,
        "w",
        encoding="utf-8"
    ) as f:

        for article in cleaned_articles:

            text = article["text"].strip()

            if text:

                f.write(text)
                f.write("\n\n")

    # ========================================================
    # Final statistics
    # ========================================================

    total_words = 0
    total_chars = 0

    for article in cleaned_articles:

        text = article["text"]

        total_words += len(text.split())
        total_chars += len(text)

    print()
    print("=" * 60)
    print("APP CLEANING COMPLETE")
    print("=" * 60)

    print(f"Raw records:              {len(articles):,}")
    print(f"Archive pages removed:    {archive_removed:,}")
    print(f"Empty records removed:    {empty_removed:,}")
    print(f"Duplicate articles removed: {duplicate_removed:,}")
    print(f"Clean articles:           {len(cleaned_articles):,}")

    print()
    print(f"Total words:              {total_words:,}")
    print(f"Total characters:         {total_chars:,}")

    print()
    print("Output JSONL:")
    print(OUTPUT_JSONL)

    print()
    print("Output TXT:")
    print(OUTPUT_TXT)


if __name__ == "__main__":
    main()