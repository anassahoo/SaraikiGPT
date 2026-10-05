import json
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://saraiki.app.com.pk"

CATEGORY_URL = (
    "https://saraiki.app.com.pk/"
    "saraiki/national/page/{}/"
)

# Start with a limited range first.
START_PAGE = 1
END_PAGE = 500

REQUEST_DELAY = 1.0
MAX_RETRIES = 3

HEADERS = {
    "User-Agent": (
        "SaraikiGPT/0.1 "
        "(academic research project for Saraiki language modeling)"
    )
}


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    ROOT
    / "data"
    / "raw"
    / "news"
    / "app_saraiki"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = OUTPUT_DIR / "articles.jsonl"

PROGRESS_FILE = OUTPUT_DIR / "progress.json"


# ============================================================
# SESSION
# ============================================================

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# HTTP REQUEST
# ============================================================

def get_soup(url):

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            response = session.get(
                url,
                timeout=30
            )

            response.raise_for_status()

            return BeautifulSoup(
                response.text,
                "html.parser"
            )

        except requests.RequestException as e:

            print(
                f"Request failed "
                f"(attempt {attempt}/{MAX_RETRIES})"
            )

            print(e)

            if attempt < MAX_RETRIES:
                time.sleep(3)

    return None


# ============================================================
# LOAD EXISTING ARTICLES
# ============================================================

def load_existing_articles():

    existing_urls = set()

    if not OUTPUT_FILE.exists():
        return existing_urls

    with open(
        OUTPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            try:

                record = json.loads(line)

                url = record.get("url")

                if url:
                    existing_urls.add(url)

            except json.JSONDecodeError:
                continue

    return existing_urls


# ============================================================
# LOAD PROGRESS
# ============================================================

def load_progress():

    if not PROGRESS_FILE.exists():
        return START_PAGE

    try:

        with open(
            PROGRESS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        return data.get(
            "next_page",
            START_PAGE
        )

    except Exception:
        return START_PAGE


# ============================================================
# SAVE PROGRESS
# ============================================================

def save_progress(next_page):

    data = {
        "next_page": next_page
    }

    with open(
        PROGRESS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2
        )


# ============================================================
# DISCOVER ARTICLES
# ============================================================

def discover_article_links(page_number):

    url = CATEGORY_URL.format(
        page_number
    )

    print(
        f"\nScanning archive page "
        f"{page_number}"
    )

    soup = get_soup(url)

    if soup is None:
        return set()

    links = set()

    for a in soup.find_all(
        "a",
        href=True
    ):

        href = a["href"]

        full_url = urljoin(
            BASE_URL,
            href
        )

        full_url = (
            full_url
            .split("#")[0]
            .split("?")[0]
        )

        parts = (
            full_url
            .rstrip("/")
            .split("/")
        )

        if not parts:
            continue

        article_id = parts[-1]

        if (
            article_id.isdigit()
            and "/saraiki/" in full_url
        ):

            links.add(
                full_url.rstrip("/") + "/"
            )

    return links


# ============================================================
# ARTICLE EXTRACTION
# ============================================================

def extract_article(url):

    soup = get_soup(url)

    if soup is None:
        return None


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title_tag = soup.find("h1")

    if not title_tag:
        return None

    title = title_tag.get_text(
        " ",
        strip=True
    )

    if not title:
        return None


    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    date = None

    time_tag = soup.find("time")

    if time_tag:

        date = (
            time_tag.get("datetime")
            or time_tag.get_text(
                " ",
                strip=True
            )
        )


    # --------------------------------------------------------
    # ARTICLE BODY
    # --------------------------------------------------------

    paragraphs = []

    for p in soup.find_all("p"):

        text = p.get_text(
            " ",
            strip=True
        )

        text = " ".join(
            text.split()
        )

        # Ignore tiny footer/menu text
        if len(text) < 40:
            continue

        paragraphs.append(text)


    # --------------------------------------------------------
    # REMOVE DUPLICATE PARAGRAPHS
    # --------------------------------------------------------

    clean_paragraphs = []

    seen = set()

    for paragraph in paragraphs:

        if paragraph not in seen:

            seen.add(paragraph)

            clean_paragraphs.append(
                paragraph
            )


    text = "\n\n".join(
        clean_paragraphs
    ).strip()


    # Ignore broken pages
    if len(text) < 100:
        return None


    # --------------------------------------------------------
    # ARTICLE ID
    # --------------------------------------------------------

    article_id = (
        url.rstrip("/")
        .split("/")[-1]
    )


    return {

        "source": "app_saraiki",

        "article_id": article_id,

        "url": url,

        "title": title,

        "date": date,

        "text": text
    }


# ============================================================
# SAVE ARTICLE IMMEDIATELY
# ============================================================

def save_article(article):

    with open(
        OUTPUT_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(
                article,
                ensure_ascii=False
            )
            + "\n"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "SaraikiGPT - APP Saraiki Collector"
    )

    print("=" * 60)


    existing_urls = (
        load_existing_articles()
    )

    print(
        f"Existing articles: "
        f"{len(existing_urls)}"
    )


    current_page = load_progress()

    if current_page < START_PAGE:
        current_page = START_PAGE


    print(
        f"Starting from archive page: "
        f"{current_page}"
    )


    new_articles = 0

    duplicate_articles = 0

    failed_articles = 0


    # ========================================================
    # ARCHIVE PAGES
    # ========================================================

    for page in range(
        current_page,
        END_PAGE + 1
    ):

        links = discover_article_links(
            page
        )


        print(
            f"Found {len(links)} "
            f"article URLs."
        )


        # ----------------------------------------------------
        # DOWNLOAD ARTICLES
        # ----------------------------------------------------

        for url in sorted(links):

            if url in existing_urls:

                duplicate_articles += 1

                print(
                    f"Already downloaded: "
                    f"{url}"
                )

                continue


            try:

                article = extract_article(
                    url
                )

                if article:

                    save_article(article)

                    existing_urls.add(url)

                    new_articles += 1

                    print(
                        "Saved:"
                    )

                    print(
                        article["title"]
                    )

                else:

                    failed_articles += 1

                    print(
                        f"Invalid article: "
                        f"{url}"
                    )


            except Exception as e:

                failed_articles += 1

                print(
                    f"Failed: {url}"
                )

                print(e)


            time.sleep(
                REQUEST_DELAY
            )


        # ----------------------------------------------------
        # SAVE PAGE PROGRESS
        # ----------------------------------------------------

        save_progress(
            page + 1
        )

        print(
            f"\nFinished archive "
            f"page {page}"
        )

        print(
            f"Total stored articles: "
            f"{len(existing_urls)}"
        )


        time.sleep(
            REQUEST_DELAY
        )


    # ========================================================
    # FINAL REPORT
    # ========================================================

    print("\n" + "=" * 60)

    print(
        "Collection completed."
    )

    print(
        f"New articles: "
        f"{new_articles}"
    )

    print(
        f"Already existing: "
        f"{duplicate_articles}"
    )

    print(
        f"Failed/invalid: "
        f"{failed_articles}"
    )

    print(
        f"Total articles stored: "
        f"{len(existing_urls)}"
    )

    print(
        f"Dataset:"
    )

    print(
        OUTPUT_FILE
    )

    print("=" * 60)


if __name__ == "__main__":
    main()