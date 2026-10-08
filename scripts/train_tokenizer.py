from pathlib import Path

from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace


ROOT = Path(__file__).resolve().parent.parent

CORPUS_FILE = ROOT / "data" / "processed" / "saraiki_corpus.txt"

TOKENIZER_DIR = ROOT / "data" / "processed" / "tokenizer"
TOKENIZER_FILE = TOKENIZER_DIR / "saraiki_bpe.json"

VOCAB_SIZE = 8000

SPECIAL_TOKENS = [
    "<PAD>",
    "<UNK>",
    "<BOS>",
    "<EOS>",
]


def main():

    if not CORPUS_FILE.exists():
        raise FileNotFoundError(
            f"Corpus not found: {CORPUS_FILE}"
        )

    TOKENIZER_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Training Saraiki BPE tokenizer")
    print("=" * 60)

    print(f"Corpus:       {CORPUS_FILE}")
    print(f"Vocabulary:   {VOCAB_SIZE}")
    print(f"Output:       {TOKENIZER_FILE}")
    print()

    tokenizer = Tokenizer(BPE(unk_token="<UNK>"))

    tokenizer.pre_tokenizer = Whitespace()

    trainer = BpeTrainer(
        vocab_size=VOCAB_SIZE,
        special_tokens=SPECIAL_TOKENS,
        show_progress=True,
    )

    tokenizer.train(
        files=[str(CORPUS_FILE)],
        trainer=trainer,
    )

    tokenizer.save(str(TOKENIZER_FILE))

    print()
    print("=" * 60)
    print("Tokenizer training completed")
    print("=" * 60)

    print(f"Vocabulary size: {tokenizer.get_vocab_size()}")
    print(f"Saved to:       {TOKENIZER_FILE}")


if __name__ == "__main__":
    main()