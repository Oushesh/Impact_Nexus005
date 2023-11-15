import subprocess
from datetime import datetime
from pathlib import Path

import srsly
import typer
import wikipediaapi

CATEGORIES = [
    # Environment
    "Category:Sustainability",
    "Category:Human impact on the environment",
    "Category:Climate change",
    "Category:Pollution",
    "Category:Global warming",
    "Category:Natural resources",
    # "Category:Manufacturing",
    # "Category:Industrial processes",
    # "Category:Primary industries",
    # "Category:Service industries",
    # "Category:Industries (economics)",
    # Both
    "Category:Sustainable Development Goals",
    # "Category:Urbanization",
    # Social
    # "Category:Clinical medicine",
    # "Category:Demographics",
    "Category:Social issues",
    # "Category:Public policy",
    # "Category:Workplace",
    "Category:Labor",
    "Category:Poverty",
    "Category:Human rights",
    "Category:Gender equality",
    # "Category:Pedagogy",
    # "Category:Working conditions",
    # "Category:Computing and society",
    # "Category:Diversity in computing",
    # "Category:Majority–minority relations",
    # "Category:Technology in society",
]


def print_categorymembers(categorymembers, level=0, max_level=1, ids={}, path=[]):
    git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"])
    git_hash = git_hash.strip().decode()
    git_origin = subprocess.check_output(["git", "remote", "get-url", "origin"])
    git_origin = git_origin.strip().decode()

    for c in categorymembers.values():
        print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
        if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
            yield from print_categorymembers(
                c.categorymembers,
                level=level + 1,
                max_level=max_level,
                ids=ids,
                path=path + [c.displaytitle],
            )
        elif c.ns == wikipediaapi.Namespace.MAIN:
            if c.pageid in ids:
                continue
            else:
                ids.add(c.pageid)
            yield {
                "url": c.fullurl,
                "text": c.text,
                "title": c.displaytitle,
                "type": "wikipedia",
                "path": path,
                "crawler": "wikipedia",
                "scrape_date": datetime.utcnow().isoformat(),
                "meta": {
                    "pageid": c.pageid,
                    "level": level,
                    "categories": c.categories,
                    "links": [[title, link.pageid] for title, link in c.links.items()],
                    "backlinks": [
                        [title, link.pageid] for title, link in c.backlinks.items()
                    ],
                    "git_origin": git_origin,
                    "git_hash": git_hash,
                },
            }


def download_category(category, max_level=3):
    category_file_path = f"wiki-{category.split(':')[-1]}.jsonl"
    ids = set()
    if Path(category_file_path).exists():
        ids = {item["meta"]["pageid"] for item in srsly.read_jsonl(category_file_path)}
    if ids:
        print(f"ALREADY DOWNLOADED {len(ids)}, CONTINUING")

    wiki_wiki = wikipediaapi.Wikipedia("en")
    cat = wiki_wiki.page(category)
    return (
        page_item
        for page_item in print_categorymembers(
            cat.categorymembers, max_level=max_level, ids=ids
        )
    )


def download_categories(categories=CATEGORIES, max_level=5):
    for category in categories:
        category_file_path = f"wiki-{category.split(':')[-1]}.jsonl"

        srsly.write_jsonl(
            category_file_path, download_category(category, max_level), append=True
        )


if __name__ == "__main__":
    typer.run(download_categories)
