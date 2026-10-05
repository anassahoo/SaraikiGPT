import requests
import json
import time
from pathlib import Path


API_URL = "https://incubator.wikimedia.org/w/api.php"

HEADERS = {
    "User-Agent": (
        "SaraikiGPT/0.1 "
        "(research project for Saraiki language modeling; "
        "contact: your-email@example.com)"
    )
}

PROJECTS = {
    "wikibooks": "Wb/skr/",
    "wikivoyage": "Wy/skr/"
}

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "data" / "raw" / "wikimedia"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_page_titles(prefix):
    titles = []
    continue_token = None

    while True:
        params = {
            "action": "query",
            "format": "json",
            "list": "allpages",
            "apprefix": prefix,
            "apnamespace": 0,
            "aplimit": "max"
        }

        if continue_token:
            params["apcontinue"] = continue_token

        response = requests.get(
            API_URL,
            params=params,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        for page in data["query"]["allpages"]:
            titles.append(page["title"])

        if "continue" not in data:
            break

        continue_token = data["continue"]["apcontinue"]

        time.sleep(0.5)

    return titles


def get_page_text(title):
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "redirects": True,
        "titles": title
    }

    response = requests.get(
        API_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    pages = data["query"]["pages"]

    page = next(iter(pages.values()))

    return page.get("extract", "")


def save_records(records, project_name):
    output_file = (
        OUTPUT_DIR
        / f"saraiki_{project_name}.jsonl"
    )

    with open(
        output_file,
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

    print(
        f"\nSaved {len(records)} pages to:"
    )
    print(output_file)


def collect_project(project_name, prefix):

    print("\n" + "=" * 50)
    print(f"Collecting: {project_name}")
    print("=" * 50)

    try:
        titles = get_page_titles(prefix)

    except requests.RequestException as e:
        print("Failed to retrieve page list.")
        print(e)
        return

    print(
        f"Found {len(titles)} pages."
    )

    records = []

    for i, title in enumerate(
        titles,
        start=1
    ):

        try:
            text = get_page_text(title)

            if text.strip():

                records.append({
                    "source": project_name,
                    "title": title,
                    "text": text
                })

                print(
                    f"[{i}/{len(titles)}] "
                    f"Downloaded: {title}"
                )

            else:
                print(
                    f"[{i}/{len(titles)}] "
                    f"Empty page: {title}"
                )

        except requests.RequestException as e:

            print(
                f"[{i}/{len(titles)}] "
                f"Failed: {title}"
            )

            print(e)

        time.sleep(0.3)

    save_records(
        records,
        project_name
    )


def main():

    print(
        "Starting Saraiki Wikimedia collection..."
    )

    for project_name, prefix in PROJECTS.items():

        collect_project(
            project_name,
            prefix
        )

    print("\nCollection completed.")


if __name__ == "__main__":
    main()