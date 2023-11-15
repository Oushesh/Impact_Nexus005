from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional
from datetime import date


@dataclass
class ScrapedDocument:
    uri: str  # unique identifier, url for websites, pdf fingerprint for pdfs
    url: str
    scraper: str  # name of scraper
    meta: Dict[str, Any]  # Any metadata that is not represented in the schema
    scrape_date: date
    text: str  # text content, extracted using trafilatura
    title: str

    # For full crawlers that are storing raw document (html, pdf), xml extracted from pdf and the final text extracted
    # Not relevant for API test
    type: Optional[str]  # pdf, html
    storage_url: Optional[str]
    text_storage_url: Optional[str]
    xml_storage_url: Optional[str]
