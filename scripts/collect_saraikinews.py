import json
import time
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_ARTICLE_URL = "https://sarikinews.com/article.php?id={}"

# Start small first.
# After confirming it works, increase MAX_ARTICLE_ID.
MIN_ARTICLE_ID = 1
MAX_ARTICLE_ID = 30

REQUEST_DELAY = 0.5

HEADERS = {
    "User-Agent": (
        "SaraikiGPT/0.1 "
        "(academic/research project for Saraiki language modeling)"
    )
}

ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    ROOT
    / "data"
    / "raw"
    / "news"
    / "saraikinews"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "articles.jsonl"


# --------------------------------------------------
# REQUEST SESSION
# --------------------------------------------------

session = requests.Session()
session.headers.update(HEADERS)


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def clean_text(text):
    """
    Remove unnecessary spaces while preserving
    paragraph boundaries.
    """

    text = text.replace("\xa0", " ")

    lines = []

    for line in text.splitlines():

        line = re.sub(r"\s+", " ", line).strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


def get_soup(url):

    response = session.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return BeautifulSoup(
        response.text,
        "html.parser"
    )


# --------------------------------------------------
# ARTICLE EXTRACTION
# --------------------------------------------------

def extract_article(article_id):

    url = BASE_ARTICLE_URL.format(article_id)

    soup = get_soup(url)

    # ----------------------------------------------
    # TITLE
    # ----------------------------------------------

    h1_tags = soup.find_all("h1")

    title = None

    for h1 in h1_tags:

        candidate = clean_text(
            h1.get_text(" ", strip=True)
        )

        # Ignore website title
        if (
            candidate
            and "سرائیکی نیوز ٹی وی" not in candidate
        ):
            title = candidate
            break

    if not title:
        return None


    # ----------------------------------------------
    # CATEGORY + DATE
    # ----------------------------------------------

    page_text = soup.get_text(
        "\n",
        strip=True
    )

    lines = [
        clean_text(line)
        for line in page_text.splitlines()
        if clean_text(line)
    ]

    category = None
    date = None

    # Usually appears directly before article title:
    #
    # کھیل · 29 Aug 2026 08:20
    # کنگ بھائی آج تو کچھ کر لیتے

    try:

        title_index = lines.index(title)

        if title_index > 0:

            metadata_line = lines[
                title_index - 1
            ]

            if "·" in metadata_line:

                parts = [
                    x.strip()
                    for x in metadata_line.split(
                        "·",
                        maxsplit=1
                    )
                ]

                if len(parts) == 2:

                    category = parts[0]
                    date = parts[1]

    except ValueError:

        title_index = -1


    # ----------------------------------------------
    # ARTICLE BODY
    # ----------------------------------------------

    paragraphs = []

    # First attempt:
    # collect <p> elements after the article title.

    title_element = None

    for h1 in h1_tags:

        if clean_text(
            h1.get_text(" ", strip=True)
        ) == title:

            title_element = h1
            break


    if title_element:

        for element in title_element.find_all_next():

            # Stop when footer starts
            element_text = clean_text(
                element.get_text(
                    " ",
                    strip=True
                )
            )

            if (
                element_text
                == "سرائیکی نیوز ٹی وی"
                and element.name != "h1"
            ):
                break

            if element.name == "p":

                text = clean_text(
                    element.get_text(
                        " ",
                        strip=True
                    )
                )

                if (
                    text
                    and text not in paragraphs
                ):
                    paragraphs.append(text)


    # ----------------------------------------------
    # FALLBACK
    # ----------------------------------------------

    # Some pages may not use <p> correctly.
    # In that case extract lines between title
    # and footer.

    if not paragraphs and title_index != -1:

        ignored_lines = {
            "Saraiki News TV",
            "LIVE TV",
            "▶ LIVE TV",
            "سرائیکی وسیب دی آواز",
        }

        for line in lines[
            title_index + 1:
        ]:

            if line == "سرائیکی نیوز ٹی وی":
                break

            if line in ignored_lines:
                continue

            # Ignore very short navigation text
            if len(line) < 20:
                continue

            paragraphs.append(line)


    # ----------------------------------------------
    # REMOVE DUPLICATES
    # ----------------------------------------------

    unique_paragraphs = []

    seen = set()

    for paragraph in paragraphs:

        if paragraph not in seen:

            seen.add(paragraph)
            unique_paragraphs.append(
                paragraph
            )


    article_text = "\n\n".join(
        unique_paragraphs
    ).strip()


    # Reject pages without meaningful content

    if len(article_text) < 100:
        return None


    return {

        "source": "saraikinews",

        "article_id": article_id,

        "url": url,

        "category": category,

        "date": date,

        "title": title,

        "text": article_text
    }


# --------------------------------------------------
# MAIN CRAWLER
# --------------------------------------------------

def main():

    print(
        "Starting historical Saraiki News collection..."
    )

    print(
        f"Scanning article IDs "
        f"{MIN_ARTICLE_ID} to "
        f"{MAX_ARTICLE_ID}"
    )

    records = []

    failed = 0
    skipped = 0


    for article_id in range(
        MIN_ARTICLE_ID,
        MAX_ARTICLE_ID + 1
    ):

        try:

            article = extract_article(
                article_id
            )

            if article:

                records.append(
                    article
                )

                print(
                    f"[ID {article_id}] "
                    f"Saved: "
                    f"{article['title']}"
                )

            else:

                skipped += 1

                print(
                    f"[ID {article_id}] "
                    f"No valid article"
                )


        except requests.RequestException as e:

            failed += 1

            print(
                f"[ID {article_id}] "
                f"Request failed: {e}"
            )


        except Exception as e:

            failed += 1

            print(
                f"[ID {article_id}] "
                f"Unexpected error: {e}"
            )


        time.sleep(
            REQUEST_DELAY
        )


    # ----------------------------------------------
    # SAVE JSONL
    # ----------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for record in records:

            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                )
                + "\n"
            )


    print("\n" + "=" * 55)

    print("Collection completed.")

    print(
        f"Valid articles: {len(records)}"
    )

    print(
        f"Skipped IDs: {skipped}"
    )

    print(
        f"Failed requests: {failed}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    print("=" * 55)


if __name__ == "__main__":
    main()