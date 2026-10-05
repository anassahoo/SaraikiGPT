import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "data" / "extracted" / "app_saraiki_clean.jsonl"

TARGET_IDS = {
    "730715",
    "730743",
    "725273",
    "725392",
    "729498",
}


def normalize(text):
    return " ".join(text.split())


def main():

    records = {}

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)

            article_id = str(record.get("article_id", ""))

            if article_id in TARGET_IDS:
                records[article_id] = record

    print("Loaded target articles:", len(records))

    for article_id in TARGET_IDS:

        if article_id not in records:
            print(f"\nArticle {article_id}: NOT FOUND")
            continue

        record = records[article_id]
        text = normalize(record.get("text", ""))

        words = text.split()

        print("\n" + "=" * 100)
        print("ARTICLE ID:", article_id)
        print("TITLE:", record.get("title", ""))
        print("WORD COUNT:", len(words))
        print("=" * 100)

        # Print first 20 sentences approximately
        sentences = []
        current = []

        for word in words:
            current.append(word)

            if word.endswith(("۔", "؟", "!", "?")):
                sentences.append(" ".join(current))
                current = []

        if current:
            sentences.append(" ".join(current))

        print("\n--- FIRST 20 SENTENCES ---")

        for i, sentence in enumerate(sentences[:20], start=1):
            print(f"\n[{i}] {sentence}")

        print("\n--- POSSIBLE REPEATED SENTENCES ---")

        seen = {}

        for i, sentence in enumerate(sentences):

            key = normalize(sentence)

            if len(key) < 30:
                continue

            if key in seen:

                print(
                    f"\nRepeated sentence:"
                    f"\nFirst position: {seen[key]}"
                    f"\nSecond position: {i}"
                    f"\nText: {sentence}"
                )

            else:
                seen[key] = i


if __name__ == "__main__":
    main()