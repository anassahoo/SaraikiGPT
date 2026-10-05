from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT
    / "data"
    / "extracted"
    / "saraiki_sacor.txt"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "extracted"
    / "saraiki_sacor_clean.txt"
)


def normalize_text(text):
    """
    Normalize whitespace without changing the
    actual Saraiki content.
    """

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Collapse spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def main():

    print("=" * 70)
    print("SACOR CLEANING")
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

    input_lines = 0
    empty_lines = 0
    output_lines = 0

    input_words = 0
    output_words = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

        for line in infile:

            input_lines += 1

            original_text = line.strip()

            if not original_text:
                empty_lines += 1
                continue

            input_words += len(
                original_text.split()
            )

            cleaned_text = normalize_text(
                original_text
            )

            if not cleaned_text:
                empty_lines += 1
                continue

            outfile.write(
                cleaned_text + "\n"
            )

            output_lines += 1

            output_words += len(
                cleaned_text.split()
            )

    print()
    print("=" * 70)
    print("CLEANING COMPLETED")
    print("=" * 70)

    print(f"Input lines:          {input_lines:,}")
    print(f"Empty lines removed:  {empty_lines:,}")
    print(f"Output sentences:     {output_lines:,}")

    print()
    print(f"Input words:          {input_words:,}")
    print(f"Output words:         {output_words:,}")
    print(
        f"Words removed:        "
        f"{input_words - output_words:,}"
    )

    print()
    print("Original file was NOT modified.")
    print("Cleaned file:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()