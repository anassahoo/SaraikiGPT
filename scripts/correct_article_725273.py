import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "data" / "extracted" / "app_saraiki_clean.jsonl"
OUTPUT_FILE = ROOT / "data" / "extracted" / "app_saraiki_corrected.jsonl"

TARGET_ARTICLE_ID = "725273"

# Sentence numbers are 1-based.
DELETE_START = 153
DELETE_END = 242


def split_sentences(text):
    sentences = re.split(r"(?<=[۔!?؟])\s+", text)

    return [
        s.strip()
        for s in sentences
        if s.strip()
    ]


def process_article(record):

    if str(record.get("article_id")) != TARGET_ARTICLE_ID:
        return record

    text = record.get("text", "")

    sentences = split_sentences(text)

    print("=" * 80)
    print("CORRECTING ARTICLE:", TARGET_ARTICLE_ID)
    print("=" * 80)

    print("Original sentences:", len(sentences))
    print("Original words:", len(text.split()))

    # Convert 1-based sentence numbers to Python indexes.
    start_index = DELETE_START - 1
    end_index = DELETE_END

    # Remove only sentences 153–242.
    corrected_sentences = (
        sentences[:start_index]
        + sentences[end_index:]
    )

    corrected_text = "\n\n".join(corrected_sentences)

    record["text"] = corrected_text

    print("Removed sentences:", DELETE_END - DELETE_START + 1)
    print("Corrected sentences:", len(corrected_sentences))
    print("Corrected words:", len(corrected_text.split()))

    return record


def main():

    print("Loading:")
    print(INPUT_FILE)

    records = []
    target_found = False

    with open(INPUT_FILE, "r", encoding="utf-8") as f:

        for line in f:

            record = json.loads(line)

            if str(record.get("article_id")) == TARGET_ARTICLE_ID:
                target_found = True
                record = process_article(record)

            records.append(record)

    if not target_found:
        print()
        print("ERROR: Target article was not found.")
        return

    # Safety: never overwrite the cleaned dataset.
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        for record in records:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                )
                + "\n"
            )

    print()
    print("=" * 80)
    print("CORRECTION COMPLETED")
    print("=" * 80)

    print("Articles written:", len(records))
    print("Output:")
    print(OUTPUT_FILE)

    print()
    print("Original file was NOT modified:")
    print(INPUT_FILE)


if __name__ == "__main__":
    main()