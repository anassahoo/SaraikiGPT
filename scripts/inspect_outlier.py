import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT
    / "data"
    / "extracted"
    / "app_saraiki_clean.jsonl"
)

TARGET_URL = "https://saraiki.app.com.pk/saraiki/725273/"


def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:

        for line in f:

            article = json.loads(line)

            if article.get("url") == TARGET_URL:

                text = article.get("text", "")

                words = text.split()

                print("=" * 80)
                print("TARGET ARTICLE")
                print("=" * 80)

                print()
                print("Title:")
                print(article.get("title", ""))

                print()
                print("URL:")
                print(article.get("url", ""))

                print()
                print("Article ID:")
                print(article.get("article_id", ""))

                print()
                print("Date:")
                print(article.get("date", ""))

                print()
                print("Word count:")
                print(len(words))

                print()
                print("=" * 80)
                print("FIRST 1000 WORDS")
                print("=" * 80)

                print(" ".join(words[:1000]))

                print()
                print("=" * 80)
                print("LAST 1000 WORDS")
                print("=" * 80)

                print(" ".join(words[-1000:]))

                print()
                print("=" * 80)
                print("ARTICLE FOUND")
                print("=" * 80)

                return

    print("Article not found.")


if __name__ == "__main__":
    main()