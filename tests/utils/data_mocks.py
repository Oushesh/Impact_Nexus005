from app.models.annotation import AnnotatedInsight
from app.models.documents import Document, DocumentType


def mock_insight(document):
    return AnnotatedInsight(
        text=document["text"],
        id="",
        url="",
        document_id="",
        par_index=0,
        type="pdf",
        scraper="test",
        document_source="RESEARCH",
        meta={},
        embedding=[],
        similarity_score=0.0,
        title=document["title"],
    )


def mock_document(document):
    return Document(
        text=document["text"],
        _id="",
        url="",
        uri="",
        type=document.get("type", DocumentType.pdf),
        scraper="test",
        document_source="RESEARCH",
        meta={},
        storage_url="",
        abstract="",
        referer="",
        summary=document.get("summary", ""),
    )
