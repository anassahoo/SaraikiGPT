from pathlib import Path

from tokenizers import Tokenizer


ROOT = Path(__file__).resolve().parent.parent

CORPUS_FILE = ROOT / "data" / "processed" / "saraiki_corpus.txt"
TOKENIZER_FILE = (
    ROOT
    / "data"
    / "processed"
    / "tokenizer"
    / "saraiki_bpe.json"
)


def main():

    tokenizer = Tokenizer.from_file(str(TOKENIZER_FILE))

    vocab = tokenizer.get_vocab()
    unk_id = vocab.get("<UNK>")

    total_tokens = 0
    unknown_tokens = 0
    total_words = 0
    lines = 0

    with open(CORPUS_FILE, "r", encoding="utf-8") as file:

        for line in file:

            text = line.strip()

            if not text:
                continue

            lines += 1
            total_words += len(text.split())

            encoding = tokenizer.encode(text)

            total_tokens += len(encoding.ids)

            if unk_id is not None:
                unknown_tokens += encoding.ids.count(unk_id)

    print("=" * 60)
    print("SaraikiGPT Tokenizer Quality Check")
    print("=" * 60)

    print(f"Vocabulary size:      {tokenizer.get_vocab_size():,}")
    print(f"Corpus lines:         {lines:,}")
    print(f"Corpus words:         {total_words:,}")
    print(f"Corpus tokens:        {total_tokens:,}")
    print(f"Unknown tokens:       {unknown_tokens:,}")

    if total_tokens > 0:
        unknown_percentage = (
            unknown_tokens / total_tokens
        ) * 100

        print(
            f"Unknown token rate:   "
            f"{unknown_percentage:.6f}%"
        )

    print()
    print("=" * 60)
    print("Real Saraiki Examples")
    print("=" * 60)

    examples = [
        "ساݙا پاکستان",
        "سرائیکی زبان دی مٹھاس بہت مشہور ہے",
        "ملتان سرائیکی وسیب دا اہم شہر ہے",
        "پاکستان دے لوکاں دی ثقافت بہت وݙی اے",
    ]

    for text in examples:

        encoding = tokenizer.encode(text)

        print()
        print("Text:")
        print(text)

        print("Tokens:")
        print(encoding.tokens)

        print("IDs:")
        print(encoding.ids)

        print("UNK count:")
        print(
            encoding.ids.count(unk_id)
            if unk_id is not None
            else 0
        )

    print()
    print("=" * 60)
    print("Check completed")
    print("=" * 60)


if __name__ == "__main__":
    main()