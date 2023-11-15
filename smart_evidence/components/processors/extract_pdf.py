import hashlib
import io
import logging
import os
from datetime import datetime
from typing import Any, List, Optional

import boto3
import pdfminer.pdfdocument
import pdfminer.pdfparser
import requests
import trafilatura
from lxml import etree
from pdfminer import high_level, pdfdocument, pdfparser
from pdfminer.pdfdocument import PDFNoOutlines
from pdfminer.pdftypes import resolve1

from app.models.documents import Document, ScrapeItem
from smart_evidence.components.base_component import BaseComponent
from smart_evidence.components.processors.base_processor import BaseProcessor


def get_pdf_meta(document):
    meta = {}
    for info in document.info:
        for k, v in info.items():
            if not isinstance(v, bytes):
                continue
            value = decode(v)
            if value.startswith("D:"):
                meta[k] = convert_pdf_datetime(value)
            else:
                meta[k] = value

    return meta


def get_num_pages(document):
    return {"num_pages": resolve1(document.catalog["Pages"])["Count"]}


def get_outline(document, maxlevel=5):
    try:
        pdf_outline = document.get_outlines()
    except PDFNoOutlines:
        return {}

    outline = []
    for (level, title, _, _, _) in pdf_outline:
        if level <= maxlevel:
            title_words = title.replace("\n", "").split()
            title = " ".join(title_words)
            outline.append({"level": level, "title": title})
    return {"outline": outline}


def decode(value):
    return value.decode("utf-8", "replace")


def convert_pdf_datetime(value):
    """
    Handles following types of timestamps:
    D:20200220143940Z
    D:20130501200439+01'00'
    """
    clean = value.replace("D:", "").replace("'", "")
    try:
        # parse D:20200220143940Z
        dtformat = "%Y%m%d%H%M%S%z"
        return datetime.strptime(clean, dtformat).isoformat()
    except ValueError:
        # parse D:20130501200439+01'00'
        dtformat = "%Y%m%d%H%M%S"
        try:
            return datetime.strptime(clean, dtformat).isoformat()
        except ValueError:
            return None
    except:
        return None


def get_meta(file):
    parser = pdfparser.PDFParser(file)
    document = pdfdocument.PDFDocument(parser)
    meta = {}
    meta.update(get_pdf_meta(document))
    meta.update(get_num_pages(document))
    meta.update(get_outline(document))

    return meta


def hexify(byte_string):
    ba = bytearray(byte_string)

    def byte_to_hex(b):
        hex_string = hex(b)

        if hex_string.startswith("0x"):
            hex_string = hex_string[2:]

        if len(hex_string) == 1:
            hex_string = "0" + hex_string

        return hex_string

    return "".join([byte_to_hex(b) for b in ba])


def hash_of_first_kilobyte(file):
    h = hashlib.md5()
    h.update(file.read(1024))
    return h.hexdigest()


def file_id_from(file):
    """
    Return the PDF file identifier from the given file as a hex string.

    Returns None if the document doesn't contain a file identifier.

    """
    parser = pdfminer.pdfparser.PDFParser(file)
    document = pdfminer.pdfdocument.PDFDocument(parser)

    for xref in document.xrefs:
        if xref.trailer:
            trailer = xref.trailer

            try:
                id_array = trailer["ID"]
            except KeyError:
                continue

            # Resolve indirect object references.
            try:
                id_array = id_array.resolve()
            except AttributeError:
                pass

            try:
                file_id = id_array[0]
            except TypeError:
                continue

            return hexify(file_id)


def get_fingerprint(file):
    return file_id_from(file) or hash_of_first_kilobyte(file)


def get_text(filename):
    text = high_level.extract_text(filename)
    return text


def get_xmltei(file):
    response = requests.post(
        f"{os.environ['GROBID_ENDPOINT']}/api/processFulltextDocument",
        files={"input": file},
    )
    if response.status_code == 200:
        return response.content
    else:
        return None


NS = {"tei": "http://www.tei-c.org/ns/1.0"}
TAGS_TO_READ = [
    f'{{{NS["tei"]}}}p',
    f'{{{NS["tei"]}}}formula',
    f'{{{NS["tei"]}}}ref',
    f'{{{NS["tei"]}}}label',
    f'{{{NS["tei"]}}}figDesc',
    f'{{{NS["tei"]}}}note',
]
HEAD_TAGS = [
    f'{{{NS["tei"]}}}head',
]


def get_paragraphs(body_element):
    for div in body_element.findall("div", {None: "http://www.tei-c.org/ns/1.0"}):
        for paragraph in div:
            if paragraph.tag in HEAD_TAGS:
                header = trafilatura.xml.xmltotxt(paragraph, include_formatting=False)
                if header:
                    yield "# " + header
            elif paragraph.tag in TAGS_TO_READ:
                text = trafilatura.xml.xmltotxt(paragraph, include_formatting=False)
                if text:
                    yield text
        yield ""
    for figure in body_element.findall("figure", {None: "http://www.tei-c.org/ns/1.0"}):
        header = figure.find("header", {None: "http://www.tei-c.org/ns/1.0"})
        if header is not None:
            yield "# " + trafilatura.xml.xmltotxt(header, include_formatting=False)
        for child in figure:
            if child.tag in TAGS_TO_READ:
                text = trafilatura.xml.xmltotxt(child, include_formatting=False)
                if text:
                    yield text
        for row in figure.findall("./table/row", {None: "http://www.tei-c.org/ns/1.0"}):
            for cell in row.findall("./cell", {None: "http://www.tei-c.org/ns/1.0"}):
                text = trafilatura.xml.xmltotxt(cell, include_formatting=False)
                if text:
                    yield text
            yield ""
        yield ""


def content_from_xml(xml_string):
    root = etree.fromstring(xml_string)  # type: ignore
    body_element = root.find("text/body", {None: "http://www.tei-c.org/ns/1.0"})
    return "\n".join(get_paragraphs(body_element))


def abstract_from_xml(xml_string):
    root = etree.fromstring(xml_string)  # type: ignore
    abstract_element = root.find(
        "teiHeader/profileDesc/abstract", {None: "http://www.tei-c.org/ns/1.0"}
    )
    return "\n".join(get_paragraphs(abstract_element))


class ExtractPDF(BaseProcessor):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        self.s3 = boto3.resource("s3")

    def process(self, document: ScrapeItem, **kwds) -> Optional[Document]:
        s3_response = self.s3.Object(
            "ix-nexus", document.storage_url.split("s3://ix-nexus/")[-1]
        )
        file = io.BytesIO()
        s3_response.download_fileobj(file)
        file.seek(0)

        extracted_document = document.dict()

        xmltei = get_xmltei(file)
        if not xmltei:
            logging.error(f"{document} could not be extracted via GROBID.")
            extracted_document["text"] = get_text(file)

        else:
            extracted_document["text"] = content_from_xml(xmltei)
            extracted_document["abstract"] = abstract_from_xml(xmltei)

        pdf_meta = get_meta(file)
        extracted_document["meta"] = extracted_document.get("meta", {})
        extracted_document["meta"].update({"pdf": pdf_meta})
        extracted_document["uri"] = get_fingerprint(file)

        title = extracted_document.get("title", "")
        if not title:
            title = pdf_meta.get("Title", "")
        if title:
            extracted_document["title"] = title

        return Document(**extracted_document)

    def run(self, documents: List[Any], **kwds):
        processed_documents = []
        for document in documents:
            processed_document = self.process(document)
            if processed_document is not None:
                processed_documents.append(processed_document)
        return self.component.run(processed_documents, **kwds)
