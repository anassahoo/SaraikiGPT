import json
import re
from pathlib import Path
from difflib import SequenceMatcher


ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT
    / "data"
    / "extracted"
    / "app_saraiki_clean.jsonl"
)


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text):
    return [
        s.strip()
        for s in re.split(r"(?<=[۔.!؟])\s+", text)
        if s.strip()
    ]


def find_repeated_blocks(sentences, min_sentences=3):
    """
    Look for consecutive blocks of sentences that appear again
    later in the same article.

    This is detection only.
    Nothing is modified.
    """

    results = []

    n = len(sentences)

    # Start with blocks of 3-12 sentences.
    for block_size in range(3, min(12, n // 2 + 1)):

        seen = {}

        for i in range(n - block_size + 1):

            block = tuple(
                normalize(s)
                for s in sentences[i:i + block_size]
            )

            if block in seen:

                previous = seen[block]

                # Avoid overlapping matches.
                if i - previous >= block_size:

                    results.append(
                        {
                            "first_start": previous,
                            "second_start": i,
                            "sentences": block_size,
                            "text": " ".join(block),
                        }
                    )

            else:
                seen[block] = i

    # Remove smaller matches contained inside larger matches.
    unique = []

    for result in sorted(
        results,
        key=lambda x: x["sentences"],
        reverse=True
    ):

        duplicate = False

        for existing in unique:

            a1 = existing["first_start"]
            a2 = existing["first_start"] + existing["sentences"]

            b1 = result["first_start"]
            b2 = result["first_start"] + result["sentences"]

            c1 = existing["second_start"]
            c2 = existing["second_start"] + existing["sentences"]

            d1 = result["second_start"]
            d2 = result["second_start"] + result["sentences"]

            first_overlap = (
                max(a1, b1) < min(a2, b2)
            )

            second_overlap = (
                max(c1, d1) < min(c2, d2)
            )

            if first_overlap and second_overlap:
                duplicate = True
                break

        if not duplicate:
            unique.append(result)

    return unique


def main():

    print("Loading cleaned APP dataset...")
    print("Input:", INPUT_FILE)

    articles = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            articles.append(json.loads(line))

    print("Articles loaded:", f"{len(articles):,}")

    flagged_articles = []

    # ========================================================
    # Detect internal duplicate blocks
    # ========================================================

    for article in articles:

        text = str(article.get("text", "")).strip()

        if not text:
            continue

        sentences = split_sentences(text)

        if len(sentences) < 6:
            continue

        repeated_blocks = find_repeated_blocks(sentences)

        if repeated_blocks:

            flagged_articles.append(
                {
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "word_count": len(text.split()),
                    "blocks": repeated_blocks,
                }
            )

    # ========================================================
    # Report
    # ========================================================

    print()
    print("=" * 70)
    print("INTERNAL DUPLICATE DETECTION")
    print("=" * 70)

    print()
    print(
        "Articles with repeated blocks:",
        f"{len(flagged_articles):,}"
    )

    print()

    for number, article in enumerate(
        flagged_articles[:30],
        start=1
    ):

        print("-" * 70)
        print(f"ARTICLE {number}")

        print("Title:")
        print(article["title"])

        print()
        print("URL:")
        print(article["url"])

        print()
        print("Words:")
        print(f"{article['word_count']:,}")

        for block_number, block in enumerate(
            article["blocks"][:3],
            start=1
        ):

            print()
            print(
                f"Repeated block {block_number}: "
                f"{block['sentences']} sentences"
            )

            print(
                "First position:",
                block["first_start"]
            )

            print(
                "Second position:",
                block["second_start"]
            )

            print()
            print("Text:")
            print(block["text"][:1000])

    print()
    print("=" * 70)
    print("DETECTION COMPLETE")
    print("=" * 70)

    print()
    print("IMPORTANT:")
    print("No files were modified.")


if __name__ == "__main__":
    main()