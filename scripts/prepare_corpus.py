from pathlib import Path
import json


ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "saraiki_corpus.txt"

SOURCES = [
    {
        "name": "APP Saraiki",
        "path": ROOT / "data" / "extracted" / "app_saraiki_corrected.jsonl",
        "type": "jsonl",
        "field": "text",
    },
    {
        "name": "Wikibooks",
        "path": ROOT / "data" / "extracted" / "wikibooks_clean.jsonl",
        "type": "jsonl",
        "field": "text",
    },
    {
        "name": "Wikivoyage",
        "path": ROOT / "data" / "extracted" / "wikivoyage_clean.jsonl",
        "type": "jsonl",
        "field": "text",
    },
    {
        "name": "SACOR",
        "path": ROOT / "data" / "extracted" / "saraiki_sacor_clean.txt",
        "type": "txt",
        "field": None,
    },
    {
        "name": "SaraikiNews",
        "path": ROOT / "data" / "extracted" / "saraikinews_clean.jsonl",
        "type": "jsonl",
        "field": "text",
    },
]


def clean_text(text):
    """Basic whitespace normalization."""
    return " ".join(str(text).split())


def process_jsonl(source):
    """Read text from a JSONL source."""
    count = 0
    words = 0

    with open(source["path"], "r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()

            if not line:
                continue

            record = json.loads(line)
            text = record.get(source["field"], "")

            text = clean_text(text)

            if not text:
                continue

            yield text

            count += 1
            words += len(text.split())

    print(f"{source['name']}: {count:,} documents, {words:,} words")


def process_txt(source):
    """Read text from a plain-text source."""
    count = 0
    words = 0

    with open(source["path"], "r", encoding="utf-8") as infile:
        for line in infile:
            text = clean_text(line)

            if not text:
                continue

            yield text

            count += 1
            words += len(text.split())

    print(f"{source['name']}: {count:,} documents, {words:,} words")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_documents = 0
    total_words = 0

    print("Preparing Saraiki corpus...\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

        for source in SOURCES:

            if not source["path"].exists():
                print(f"WARNING: File not found: {source['path']}")
                continue

            source_documents = 0
            source_words = 0

            if source["type"] == "jsonl":
                texts = process_jsonl(source)
            else:
                texts = process_txt(source)

            for text in texts:
                outfile.write(text + "\n")

                source_documents += 1
                source_words += len(text.split())

                total_documents += 1
                total_words += len(text.split())

            print(
                f"Processed {source['name']}: "
                f"{source_documents:,} documents, "
                f"{source_words:,} words"
            )

    print("\n" + "=" * 50)
    print("Corpus preparation completed.")
    print("=" * 50)

    print(f"Total documents: {total_documents:,}")
    print(f"Total words:     {total_words:,}")
    print(f"Output file:     {OUTPUT_FILE}")


if __name__ == "__main__":
    main()