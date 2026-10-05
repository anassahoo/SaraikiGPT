# extract_sacor.py
import pandas as pd
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent.parent

input_file = ROOT / "data" / "raw" / "corpora" / "en-skr.tsv"
output_file = ROOT / "data" / "extracted" / "saraiki_sacor.txt"

# Create output folder if it does not exist
output_file.parent.mkdir(parents=True, exist_ok=True)

# Read SACOR TSV file
df = pd.read_csv(input_file, sep="\t")

# Extract only Saraiki sentences
saraiki_sentences = df["target_sentence"].dropna()

# Save one sentence per line
with open(output_file, "w", encoding="utf-8") as f:
    for sentence in saraiki_sentences:
        sentence = str(sentence).strip()

        if sentence:
            f.write(sentence + "\n")

print("Extraction completed.")
print("Total Saraiki sentences:", len(saraiki_sentences))
print("Saved to:", output_file)