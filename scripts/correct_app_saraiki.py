import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "data" / "extracted" / "app_saraiki_clean.jsonl"
OUTPUT_FILE = ROOT / "data" / "extracted" / "app_saraiki_corrected.jsonl"


def normalize_text(text):
    """Normalize whitespace without changing the actual wording."""
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text):
    """
    Basic sentence splitter for Urdu/Saraiki text.
    Keeps the original sentence wording.
    """
    parts = re.split(r"(?<=[۔!?؟])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def remove_repeated_block(text, min_size=3, max_size=12):
    """
    Remove a high-confidence repeated consecutive sentence block.

    Example:

    A
    B
    C
    D
    A
    B
    C
    D

    becomes:

    A
    B
    C
    D

    Only removes an exact consecutive repetition.
    """

    sentences = split_sentences(text)

    if len(sentences) < min_size * 2:
        return text, False

    for block_size in range(max_size, min_size - 1, -1):

        for start in range(len(sentences) - block_size * 2 + 1):

            first_block = sentences[
                start:start + block_size
            ]

            second_start = start + block_size

            second_block = sentences[
                second_start:second_start + block_size
            ]

            if first_block == second_block:

                new_sentences = (
                    sentences[:second_start]
                    + sentences[second_start + block_size:]
                )

                return " ".join(new_sentences), True

    return text, False


def main():

    print("Loading:", INPUT_FILE)

    records = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:

            line = line.strip()

            if not line:
                continue

            records.append(json.loads(line))

    print("Input records:", len(records))

    corrected = []

    corrected_articles = 0

    for record in records:

        original_text = record.get("text", "")

        if not original_text:
            continue

        text = normalize_text(original_text)

        corrected_text, changed = remove_repeated_block(text)

        if changed:
            corrected_articles += 1

        new_record = record.copy()
        new_record["text"] = corrected_text

        corrected.append(new_record)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for record in corrected:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                )
                + "\n"
            )

    print("\nCorrection completed.")
    print("Input records:", len(records))
    print("Output records:", len(corrected))
    print("Articles corrected:", corrected_articles)
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()