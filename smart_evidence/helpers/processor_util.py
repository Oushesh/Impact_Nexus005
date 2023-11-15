import json
import logging

def html_extraction_to_document(extracted_document, extraction, url):
    extracted_document["meta"] = extracted_document.get("meta", {})
    if extraction is not None:
        extraction = json.loads(extraction)
        extracted_document["title"] = extracted_document.get(
            "title", extraction["title"]
        )
        extracted_document["uri"] = extraction["fingerprint"]
        extracted_document["text"] = extraction["text"]
        extracted_document["meta"].update(
            {
                "html": {
                    k: v
                    for k, v in extraction.items()
                    if k
                    not in ["title", "fingerprint", "raw-text", "text", "comments"]
                }
            }
        )
    else:
        logging.warning(
            f"HTML document {url} could not be extracted using trafilatura"
        )
    return extracted_document