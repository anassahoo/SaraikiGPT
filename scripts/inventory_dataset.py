import json
import re
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw"
EXTRACTED_DIR = ROOT / "data" / "extracted"


# ============================================================
# HELPERS
# ============================================================

def count_words(text):
    """
    Simple whitespace-based word count.

    This is NOT tokenizer token count.
    We will calculate actual model tokens later.
    """
    return len(text.split())


def count_sentences(text):
    """
    Approximate sentence count using common
    Urdu/Saraiki sentence-ending punctuation.
    """
    sentences = re.split(r"(?<=[۔!?؟])\s+", text)

    return len([
        s for s in sentences
        if s.strip()
    ])


def create_stats(name):
    return {
        "name": name,
        "documents": 0,
        "sentences": 0,
        "words": 0,
        "characters": 0,
    }


def print_stats(stats):
    print(f"\n{stats['name']}")
    print("-" * 60)
    print(f"Documents:  {stats['documents']:,}")
    print(f"Sentences:  {stats['sentences']:,}")
    print(f"Words:      {stats['words']:,}")
    print(f"Characters: {stats['characters']:,}")


# ============================================================
# TXT FILE
# ============================================================

def analyze_txt(file_path, name):

    stats = create_stats(name)

    if not file_path.exists():
        print(f"\nSKIPPED — file not found:")
        print(file_path)
        return stats

    with open(file_path, "r", encoding="utf-8") as f:

        for line in f:

            text = line.strip()

            if not text:
                continue

            stats["documents"] += 1
            stats["sentences"] += count_sentences(text)
            stats["words"] += count_words(text)
            stats["characters"] += len(text)

    return stats


# ============================================================
# JSONL FILE
# ============================================================

def analyze_jsonl(file_path, name, text_field="text"):

    stats = create_stats(name)

    if not file_path.exists():
        print(f"\nSKIPPED — file not found:")
        print(file_path)
        return stats

    with open(file_path, "r", encoding="utf-8") as f:

        for line_number, line in enumerate(f, start=1):

            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)

            except json.JSONDecodeError:
                print(
                    f"WARNING: Invalid JSON at line "
                    f"{line_number} in {file_path}"
                )
                continue

            text = record.get(text_field, "")

            if not text:
                continue

            text = str(text).strip()

            if not text:
                continue

            stats["documents"] += 1
            stats["sentences"] += count_sentences(text)
            stats["words"] += count_words(text)
            stats["characters"] += len(text)

    return stats


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("SaraikiGPT DATASET INVENTORY")
    print("=" * 70)

    print("\nProject root:")
    print(ROOT)

    all_stats = []


    # --------------------------------------------------------
    # 1. APP SARAIKI
    # --------------------------------------------------------

    app_file = (
        EXTRACTED_DIR /
        "app_saraiki_corrected.jsonl"
    )

    app_stats = analyze_jsonl(
        app_file,
        "APP Saraiki"
    )

    all_stats.append(app_stats)


    # --------------------------------------------------------
    # 2. SACOR
    # --------------------------------------------------------

    sacor_file = (
        EXTRACTED_DIR /
        "saraiki_sacor.txt"
    )

    sacor_stats = analyze_txt(
        sacor_file,
        "SACOR"
    )

    all_stats.append(sacor_stats)


    # --------------------------------------------------------
    # 3. WIKIBOOKS
    # --------------------------------------------------------

    wikibooks_file = (
        RAW_DIR /
        "wikimedia" /
        "saraiki_wikibooks.jsonl"
    )

    wikibooks_stats = analyze_jsonl(
        wikibooks_file,
        "Wikibooks"
    )

    all_stats.append(wikibooks_stats)


    # --------------------------------------------------------
    # 4. WIKIVOYAGE
    # --------------------------------------------------------

    wikivoyage_file = (
        RAW_DIR /
        "wikimedia" /
        "saraiki_wikivoyage.jsonl"
    )

    wikivoyage_stats = analyze_jsonl(
        wikivoyage_file,
        "Wikivoyage"
    )

    all_stats.append(wikivoyage_stats)


    # --------------------------------------------------------
    # 5. SARAIKINEWS
    # --------------------------------------------------------

    saraikinews_file = (
        RAW_DIR /
        "news" /
        "saraikinews" /
        "articles.jsonl"
    )

    saraikinews_stats = analyze_jsonl(
        saraikinews_file,
        "SaraikiNews"
    )

    all_stats.append(saraikinews_stats)


    # ========================================================
    # SOURCE-BY-SOURCE RESULTS
    # ========================================================

    print("\n")
    print("=" * 70)
    print("SOURCE-BY-SOURCE RESULTS")
    print("=" * 70)

    for stats in all_stats:
        print_stats(stats)


    # ========================================================
    # TOTAL
    # ========================================================

    total = create_stats("TOTAL")

    for stats in all_stats:

        total["documents"] += stats["documents"]
        total["sentences"] += stats["sentences"]
        total["words"] += stats["words"]
        total["characters"] += stats["characters"]


    print("\n")
    print("=" * 70)
    print_stats(total)
    print("=" * 70)


    # ========================================================
    # IMPORTANT NOTE
    # ========================================================

    print("\nIMPORTANT:")
    print("Words are whitespace-based counts.")
    print("They are NOT Transformer training token counts.")
    print("Actual token count will be measured after tokenizer creation.")


if __name__ == "__main__":
    main()