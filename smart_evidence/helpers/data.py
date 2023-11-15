import hashlib
from typing import Dict


def entity_dict(ent):
    entity = dict(text=ent.text)

    if ent.kb_id_:
        entity["id"] = ent.kb_id_
        if ent.label_ == "DBPEDIA_ENT":
            entity["id"] = entity["id"].split("/")[-1]
            entity["concept_label"] = entity["id"].replace("_", " ")
    elif ent.ent_id_:
        entity["id"] = ent.ent_id_
        if ";" in entity["id"]:
            entity["concept_label"] = entity["id"].split(";")[-1]

    if ent.label_:
        entity["label"] = ent.label_

    entity["start_token"] = ent.start
    entity["end_token"] = ent.end
    entity["start_char"] = ent.start_char
    entity["end_char"] = ent.end_char
    return entity


def extract_entities(doc):
    entities = []
    for ent in set(
        list(doc.ents)
        + list(doc.spans.get("dbpedia_spotlight", []))
        + list(doc.spans.get("ents_original", []))
    ):
        entities.append(entity_dict(ent))

    return entities


def hash_documents(documents, id_field="id", fields=["url", "text"]):
    hashed_documents = []
    for document in documents:
        try:
            document[id_field] = hash_document(document, fields)
        except AssertionError as e:
            print(e)
            continue
        hashed_documents.append(document)
    return hashed_documents


def hash_document(document: Dict, fields=["url", "text"]):
    hashId = hashlib.md5()
    assert all(
        field in document for field in fields
    ), f"uri or url is required to be in the document. Document keys: {list(document.keys())}"

    hashId.update(
        repr(tuple([document.get(field, "") for field in fields])).encode("utf-8")
    )

    return hashId.hexdigest()


def filter_dups(documents):
    ids = set()
    filtered_documents = []
    for document in documents:
        if document.id in ids:
            continue
        else:
            ids.add(document.id)
            filtered_documents.append(document)

    return filtered_documents


def filter_item_fields(document, fields):
    assert isinstance(document, Dict)
    return {k: v for k, v in document.items() if k in fields}
