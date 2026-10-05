import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "wikimedia"
    / "saraiki_wikibooks.jsonl"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "extracted"
    / "wikibooks_clean.jsonl"
)


def normalize_text(text):
    """Normalize whitespace without changing the actual words."""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def remove_duplicate_lines(lines):
    """
    Remove only consecutive identical lines.

    We do NOT globally deduplicate lines because the same
    sentence may legitimately appear in different sections.
    """

    cleaned = []

    previous = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if line == previous:
            continue

        cleaned.append(line)
        previous = line

    return cleaned


def clean_record(record):

    text = record.get("text", "")

    if not text:
        return None

    text = normalize_text(str(text))

    if not text:
        return None

    lines = text.split("\n")

    lines = remove_duplicate_lines(lines)

    text = "\n".join(lines).strip()

    if not text:
        return None

    cleaned_record = record.copy()
    cleaned_record["text"] = text

    return cleaned_record


def main():

    print("=" * 70)
    print("WIKIBOOKS CLEANING")
    print("=" * 70)

    print("Input:")
    print(INPUT_FILE)

    print("Output:")
    print(OUTPUT_FILE)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    total = 0
    cleaned = 0
    removed = 0

    input_words = 0
    output_words = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

        for line in infile:

            if not line.strip():
                continue

            total += 1

            record = json.loads(line)

            original_text = str(
                record.get("text", "")
            )

            input_words += len(
                original_text.split()
            )

            cleaned_record = clean_record(record)

            if cleaned_record is None:
                removed += 1
                continue

            cleaned_text = cleaned_record["text"]

            output_words += len(
                cleaned_text.split()
            )

            outfile.write(
                json.dumps(
                    cleaned_record,
                    ensure_ascii=False
                )
                + "\n"
            )

            cleaned += 1

    print()
    print("=" * 70)
    print("CLEANING COMPLETED")
    print("=" * 70)

    print(f"Input documents:      {total:,}")
    print(f"Clean documents:      {cleaned:,}")
    print(f"Removed documents:    {removed:,}")
    print(f"Input words:          {input_words:,}")
    print(f"Output words:         {output_words:,}")
    print(
        f"Words removed:        "
        f"{input_words - output_words:,}"
    )

    print()
    print("Raw file was NOT modified.")
    print("Cleaned file:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()