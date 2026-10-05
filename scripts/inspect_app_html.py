import requests
from bs4 import BeautifulSoup
from pathlib import Path

URLS = [
    "https://saraiki.app.com.pk/saraiki/730715/",
    "https://saraiki.app.com.pk/saraiki/725273/",
]

HEADERS = {
    "User-Agent": (
        "SaraikiGPT/0.1 "
        "(research project for Saraiki language modeling; "
        "contact: your-email@example.com)"
    )
}


def describe_element(element):
    """Return a compact description of an HTML element."""
    if not element:
        return "None"

    tag = element.name
    element_id = element.get("id")
    classes = element.get("class")

    parts = [tag]

    if element_id:
        parts.append(f"#{element_id}")

    if classes:
        parts.append("." + ".".join(classes))

    return "".join(parts)


def parent_chain(element, levels=5):
    """Show the parent hierarchy."""
    chain = []

    current = element

    for _ in range(levels):
        if current is None:
            break

        chain.append(describe_element(current))
        current = current.parent

    return " <- ".join(chain)


def inspect_article(url):
    print("\n" + "=" * 100)
    print("URL:", url)
    print("=" * 100)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    print("HTTP status:", response.status_code)

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # ---------------------------------------------------------
    # 1. Find title
    # ---------------------------------------------------------

    print("\n--- TITLES ---")

    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(" ", strip=True)

        if text:
            print(
                describe_element(tag),
                "=>",
                text[:200]
            )

    # ---------------------------------------------------------
    # 2. Inspect all paragraphs
    # ---------------------------------------------------------

    paragraphs = soup.find_all("p")

    print("\n--- PARAGRAPHS ---")
    print("Total <p> elements:", len(paragraphs))

    for i, p in enumerate(paragraphs):
        text = p.get_text(" ", strip=True)

        if not text:
            continue

        print(f"\nP[{i}]")
        print("Element:", describe_element(p))
        print("Parents:", parent_chain(p, 6))
        print("Text:", text[:250])

    # ---------------------------------------------------------
    # 3. Find containers containing many paragraphs
    # ---------------------------------------------------------

    print("\n--- POSSIBLE ARTICLE CONTAINERS ---")

    candidates = []

    for tag in soup.find_all(["article", "section", "div", "main"]):

        child_paragraphs = tag.find_all("p")

        if len(child_paragraphs) >= 3:

            text = tag.get_text(" ", strip=True)

            candidates.append(
                (
                    len(child_paragraphs),
                    describe_element(tag),
                    text[:200]
                )
            )

    # Sort largest paragraph containers first
    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    for count, element, preview in candidates[:30]:

        print("\nContainer:", element)
        print("Paragraph count:", count)
        print("Preview:", preview)

    # ---------------------------------------------------------
    # 4. Save raw HTML for manual inspection
    # ---------------------------------------------------------

    output_dir = Path("data") / "extracted" / "html_debug"
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    article_id = url.rstrip("/").split("/")[-1]

    output_file = output_dir / f"{article_id}.html"

    output_file.write_text(
        response.text,
        encoding="utf-8"
    )

    print("\nSaved HTML:")
    print(output_file)


def main():

    for url in URLS:
        try:
            inspect_article(url)

        except Exception as e:
            print("\nERROR:")
            print(type(e).__name__, e)


if __name__ == "__main__":
    main()