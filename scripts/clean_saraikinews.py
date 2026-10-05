import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "news"
    / "saraikinews"
    / "articles.jsonl"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "extracted"
    / "saraikinews_clean.jsonl"
)


def normalize_text(text):
    """Normalize whitespace without changing the content."""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_record(record):

    cleaned = record.copy()

    text = record.get("text", "")

    if text is None:
        return None

    text = normalize_text(str(text))

    if not text:
        return None

    cleaned["text"] = text

    # Normalize title if present
    if "title" in cleaned and cleaned["title"] is not None:
        cleaned["title"] = normalize_text(
            str(cleaned["title"])
        )

    return cleaned


def main():

    print("=" * 70)
    print("SARAIKINEWS CLEANING")
    print("=" * 70)

    print("Input:")
    print(INPUT_FILE)

    print("Output:")
    print(OUTPUT_FILE)

    if not INPUT_FILE.exists():
        print("\nERROR: Input file not found.")
        return

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

            original_text = record.get("text", "")

            if original_text:
                input_words += len(
                    str(original_text).split()
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
                ) + "\n"
            )

            cleaned += 1

    print()
    print("=" * 70)
    print("CLEANING COMPLETED")
    print("=" * 70)

    print(f"Input articles:       {total:,}")
    print(f"Clean articles:       {cleaned:,}")
    print(f"Removed articles:     {removed:,}")

    print()
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