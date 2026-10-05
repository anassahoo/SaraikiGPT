import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "data" / "extracted" / "app_saraiki_clean.jsonl"

TARGET_ARTICLE_ID = "725273"


def split_sentences(text):
    import re

    sentences = re.split(r"(?<=[۔!?؟])\s+", text)

    return [
        s.strip()
        for s in sentences
        if s.strip()
    ]


with open(INPUT_FILE, "r", encoding="utf-8") as f:

    target = None

    for line in f:
        record = json.loads(line)

        if str(record.get("article_id")) == TARGET_ARTICLE_ID:
            target = record
            break


if target is None:
    print("Article not found.")
    exit()


sentences = split_sentences(target["text"])


print("=" * 100)
print("ARTICLE 725273 — DUPLICATE BOUNDARY INSPECTION")
print("=" * 100)

print("\n--- BEFORE / END OF FIRST COPY ---")

for i in range(140, 156):
    print(f"[{i + 1}] {sentences[i]}")


print("\n--- BEFORE / END OF SECOND COPY ---")

for i in range(230, 248):
    print(f"[{i + 1}] {sentences[i]}")


print("\nTotal sentences:", len(sentences))