import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "data" / "extracted" / "app_saraiki_clean.jsonl"
OUTPUT_FILE = ROOT / "data" / "extracted" / "large_duplicate_report.txt"

# Minimum number of consecutive sentences that must repeat.
MIN_BLOCK_SIZE = 3

# Maximum block size we will search for.
MAX_BLOCK_SIZE = 100

# Only report repetitions where the second copy starts
# reasonably far from the first copy.
MIN_GAP = 5


def normalize_sentence(sentence):
    return " ".join(sentence.split()).strip()


def split_sentences(text):
    """
    Basic Saraiki/Urdu sentence splitter.
    """
    sentences = []

    current = []

    for word in text.split():
        current.append(word)

        if word.endswith(("۔", "؟", "!", "?")):
            sentence = normalize_sentence(" ".join(current))

            if sentence:
                sentences.append(sentence)

            current = []

    if current:
        sentence = normalize_sentence(" ".join(current))

        if sentence:
            sentences.append(sentence)

    return sentences


def find_repeated_blocks(sentences):
    """
    Find repeated consecutive sentence blocks.

    We search from large blocks to small blocks.
    This helps identify substantial duplicated sections
    instead of isolated repeated sentences.
    """

    results = []

    n = len(sentences)

    if n < MIN_BLOCK_SIZE * 2:
        return results

    max_size = min(MAX_BLOCK_SIZE, n // 2)

    for block_size in range(max_size, MIN_BLOCK_SIZE - 1, -1):

        found_for_size = set()

        for start1 in range(n - block_size):

            block = tuple(
                sentences[start1:start1 + block_size]
            )

            if not block:
                continue

            # Ignore extremely short blocks
            if sum(len(x) for x in block) < 150:
                continue

            search_start = start1 + block_size + MIN_GAP

            for start2 in range(search_start, n - block_size + 1):

                second_block = tuple(
                    sentences[start2:start2 + block_size]
                )

                if block != second_block:
                    continue

                # Avoid reporting the same region repeatedly.
                key = (
                    start1,
                    start2,
                    block_size
                )

                if key in found_for_size:
                    continue

                found_for_size.add(key)

                results.append(
                    {
                        "start1": start1,
                        "start2": start2,
                        "size": block_size,
                        "sentences": block,
                    }
                )

                # Once a large duplicate is found,
                # don't need to report smaller blocks
                # starting at the same locations.
                break

    return results


def main():

    print("Loading:", INPUT_FILE)

    records = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if line:
                records.append(json.loads(line))

    print("Articles:", len(records))

    report = []

    total_articles_flagged = 0
    total_blocks = 0

    for record in records:

        article_id = str(
            record.get("article_id", "")
        )

        title = record.get("title", "")

        text = record.get("text", "")

        sentences = split_sentences(text)

        duplicates = find_repeated_blocks(
            sentences
        )

        if not duplicates:
            continue

        total_articles_flagged += 1
        total_blocks += len(duplicates)

        report.append(
            "\n" + "=" * 100
        )

        report.append(
            f"ARTICLE ID: {article_id}"
        )

        report.append(
            f"TITLE: {title}"
        )

        report.append(
            f"TOTAL SENTENCES: {len(sentences)}"
        )

        report.append(
            f"REPEATED BLOCKS: {len(duplicates)}"
        )

        for number, duplicate in enumerate(
            duplicates,
            start=1
        ):

            start1 = duplicate["start1"]
            start2 = duplicate["start2"]
            size = duplicate["size"]

            report.append(
                "\n" + "-" * 80
            )

            report.append(
                f"BLOCK {number}"
            )

            report.append(
                f"First position: "
                f"{start1 + 1}"
            )

            report.append(
                f"Second position: "
                f"{start2 + 1}"
            )

            report.append(
                f"Block size: "
                f"{size} sentences"
            )

            report.append(
                "\nRepeated content:"
            )

            # Show only first 10 sentences
            # of each detected block.
            for sentence in duplicate["sentences"][:10]:

                report.append(
                    "  " + sentence
                )

            if size > 10:

                report.append(
                    f"  ... "
                    f"({size - 10} more sentences)"
                )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("\nDetection completed.")
    print(
        "Articles with large repeated blocks:",
        total_articles_flagged
    )
    print(
        "Total repeated blocks:",
        total_blocks
    )
    print(
        "Report saved to:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()