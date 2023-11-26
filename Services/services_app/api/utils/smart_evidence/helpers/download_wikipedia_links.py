import srsly
import typer
import wikipediaapi

wiki_wiki = wikipediaapi.Wikipedia("en")

IDS = {item["pageid"] for item in srsly.read_jsonl("wiki.jsonl")}
CATEGORIES = [
    "Sustainable Development Goal 2"
    "Sustainable Development Goal 1"
    "Sustainable Development Goal 3"
    "Sustainable Development Goal 4"
    "Sustainable Development Goal 5"
    "Sustainable Development Goal 6"
    "Sustainable Development Goal 7"
    "Sustainable Development Goal 8"
    "Sustainable Development Goal 9"
    "Sustainable Development Goal 10"
    "Sustainable Development Goal 11"
    "Sustainable Development Goal 12"
    "Sustainable Development Goal 13"
    "Sustainable Development Goal 14"
    "Sustainable Development Goal 15"
    "Sustainable Development Goal 16"
    "Sustainable Development Goal 17"
]


def print_categorymembers(categorymembers, category, level=0, max_level=1):
    for c in categorymembers.values():
        print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
        if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
            yield from print_categorymembers(
                c.categorymembers, category, level=level + 1, max_level=max_level
            )
        elif c.ns == wikipediaapi.Namespace.MAIN:
            if c.pageid in IDS:
                continue
            else:
                IDS.add(c.pageid)
            yield {
                "id": c.fullurl,
                "text": c.text,
                "url": c.fullurl,
                "pageid": c.pageid,
                "title": c.displaytitle,
                "level": level,
                "category": category,
            }


def download_categories(categories=CATEGORIES, max_level=2):
    print(f"ALREADY DOWNLOADED {len(IDS)}, CONTINUING")
    for category in categories:
        cat = wiki_wiki.page(category)
        cat_pages_generator = (
            page_item
            for page_item in print_categorymembers(
                cat.categorymembers, category, max_level=max_level
            )
        )
        srsly.write_jsonl("wiki2.jsonl", cat_pages_generator, append=True)


if __name__ == "__main__":
    typer.run(download_categories)
