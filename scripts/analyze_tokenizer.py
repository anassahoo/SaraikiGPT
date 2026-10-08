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

    if not CORPUS_FILE.exists():
        raise FileNotFoundError(
            f"Corpus not found: {CORPUS_FILE}"
        )

    if not TOKENIZER_FILE.exists():
        raise FileNotFoundError(
            f"Tokenizer not found: {TOKENIZER_FILE}"
        )

    print("=" * 60)
    print("SaraikiGPT Tokenizer Analysis")
    print("=" * 60)

    # Load trained tokenizer
    tokenizer = Tokenizer.from_file(str(TOKENIZER_FILE))

    vocab_size = tokenizer.get_vocab_size()

    print(f"Vocabulary size: {vocab_size:,}")
    print(f"Corpus: {CORPUS_FILE}")
    print()

    total_words = 0
    total_tokens = 0
    total_lines = 0

    # Analyze the corpus line by line
    with open(CORPUS_FILE, "r", encoding="utf-8") as file:

        for line in file:

            text = line.strip()

            if not text:
                continue

            # Count whitespace-separated words
            words = text.split()
            total_words += len(words)

            # Convert text into token IDs
            encoding = tokenizer.encode(text)

            total_tokens += len(encoding.ids)

            total_lines += 1

    print("=" * 60)
    print("Corpus Statistics")
    print("=" * 60)

    print(f"Documents/lines: {total_lines:,}")
    print(f"Words:           {total_words:,}")
    print(f"Tokens:          {total_tokens:,}")

    if total_words > 0:
        tokens_per_word = total_tokens / total_words
        print(f"Tokens per word: {tokens_per_word:.4f}")

    if total_tokens > 0:
        words_per_token = total_words / total_tokens
        print(f"Words per token: {words_per_token:.4f}")

    print()

    # Show real examples
    examples = [
        "ساݙا پاکستان",
        "پاکستان بہت خوبصورت ہے",
        "سرائیکی زبان",
    ]

    print("=" * 60)
    print("Tokenization Examples")
    print("=" * 60)

    for text in examples:

        encoding = tokenizer.encode(text)

        print()
        print(f"Text:      {text}")
        print(f"Tokens:    {encoding.tokens}")
        print(f"Token IDs: {encoding.ids}")
        print(f"Count:     {len(encoding.ids)}")

    print()
    print("=" * 60)
    print("Analysis completed")
    print("=" * 60)


if __name__ == "__main__":
    main()