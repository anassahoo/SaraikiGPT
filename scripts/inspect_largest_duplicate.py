import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "data" / "extracted" / "app_saraiki_corrected.jsonl"
OUTPUT_FILE = ROOT / "data" / "extracted" / "largest_duplicate_report.txt"

TARGET_ARTICLE_ID = 725273
MIN_BLOCK_SIZE = 3


def split_sentences(text):
    """
    Split Saraiki/Urdu text approximately by sentence-ending punctuation.
    """
    sentences = re.split(r"(?<=[۔!?؟])\s+", text)

    return [
        s.strip()
        for s in sentences
        if s.strip()
    ]


def find_largest_repeated_block(sentences):
    """
    Find the longest exact repeated consecutive sentence block.

    We compare every pair of starting positions and calculate
    how many consecutive sentences are identical.
    """

    n = len(sentences)

    best = None

    for i in range(n):
        for j in range(i + 1, n):

            # The two blocks must not overlap.
            if j - i < MIN_BLOCK_SIZE:
                continue

            length = 0

            while (
                i + length < n
                and j + length < n
                and sentences[i + length] == sentences[j + length]
            ):
                length += 1

                # Don't allow the two matching regions to overlap.
                if i + length > j:
                    break

            if length >= MIN_BLOCK_SIZE:

                if best is None or length > best["length"]:
                    best = {
                        "first_start": i,
                        "second_start": j,
                        "length": length,
                    }

    return best


def main():

    print(f"Loading: {INPUT_FILE}")

    target = None

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)

            if str(record.get("article_id")) == str(TARGET_ARTICLE_ID):
                target = record
                break

    if target is None:
        print(f"Article {TARGET_ARTICLE_ID} not found.")
        return

    text = target.get("text", "")

    sentences = split_sentences(text)

    print("Article ID:", TARGET_ARTICLE_ID)
    print("Total sentences:", len(sentences))
    print("Total words:", len(text.split()))

    result = find_largest_repeated_block(sentences)

    if result is None:
        print("No large repeated block found.")
        return

    first = result["first_start"]
    second = result["second_start"]
    length = result["length"]

    print()
    print("=" * 80)
    print("LARGEST REPEATED BLOCK")
    print("=" * 80)

    print("First occurrence sentence:", first + 1)
    print("Second occurrence sentence:", second + 1)
    print("Repeated sentences:", length)

    print()
    print("=" * 80)
    print("CONTEXT BEFORE FIRST OCCURRENCE")
    print("=" * 80)

    for i in range(max(0, first - 5), first):
        print(f"[{i + 1}] {sentences[i]}")

    print()
    print("=" * 80)
    print("FIRST OCCURRENCE")
    print("=" * 80)

    for i in range(first, min(first + length, first + 10)):
        print(f"[{i + 1}] {sentences[i]}")

    if length > 10:
        print(f"... ({length - 10} more repeated sentences) ...")

    print()
    print("=" * 80)
    print("CONTEXT AFTER FIRST OCCURRENCE")
    print("=" * 80)

    for i in range(
        min(first + length, len(sentences)),
        min(first + length + 5, len(sentences))
    ):
        print(f"[{i + 1}] {sentences[i]}")

    print()
    print("=" * 80)
    print("CONTEXT BEFORE SECOND OCCURRENCE")
    print("=" * 80)

    for i in range(max(0, second - 5), second):
        print(f"[{i + 1}] {sentences[i]}")

    print()
    print("=" * 80)
    print("SECOND OCCURRENCE")
    print("=" * 80)

    for i in range(second, min(second + length, second + 10)):
        print(f"[{i + 1}] {sentences[i]}")

    if length > 10:
        print(f"... ({length - 10} more repeated sentences) ...")

    print()
    print("=" * 80)
    print("CONTEXT AFTER SECOND OCCURRENCE")
    print("=" * 80)

    for i in range(
        min(second + length, len(sentences)),
        min(second + length + 5, len(sentences))
    ):
        print(f"[{i + 1}] {sentences[i]}")

    # Save report
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        f.write(f"Article ID: {TARGET_ARTICLE_ID}\n")
        f.write(f"Total sentences: {len(sentences)}\n")
        f.write(f"Total words: {len(text.split())}\n\n")

        f.write("LARGEST REPEATED BLOCK\n")
        f.write("=" * 80 + "\n")
        f.write(f"First occurrence: sentence {first + 1}\n")
        f.write(f"Second occurrence: sentence {second + 1}\n")
        f.write(f"Repeated sentences: {length}\n\n")

        f.write("FIRST OCCURRENCE\n")
        f.write("=" * 80 + "\n")

        for i in range(first, first + length):
            f.write(f"[{i + 1}] {sentences[i]}\n")

        f.write("\nSECOND OCCURRENCE\n")
        f.write("=" * 80 + "\n")

        for i in range(second, second + length):
            f.write(f"[{i + 1}] {sentences[i]}\n")

    print()
    print("Report saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()