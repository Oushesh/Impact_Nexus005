import os
from typing import Callable, Dict, List

from dateutil import parser
from neomodel import (
    DateTimeProperty,
    RelationshipTo,
    RelationshipFrom,
    IntegerProperty,
    StringProperty,
    StructuredNode,
    config,
)

NEO4J_USER = os.environ["NEO4J_USER"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
NEO4J_URI = os.environ["NEO4J_URI"]

config.DATABASE_URL = f"bolt://{NEO4J_USER}:{NEO4J_PASSWORD}@{NEO4J_URI}"
config.ENCRYPTED_CONNECTION = False


class FromAirtable:
    __airtable_to_backend__: Dict[str, str] = {}
    __translation_functions__: Dict[str, Callable] = {}
    __lookup_fields__: List[str] = []
    __computed_fields__: List[str] = []

    @classmethod
    def from_airtable(cls, id, fields, **kwargs):
        fields = {
            cls.__airtable_to_backend__[k]: v
            for k, v in fields.items()
            if k in cls.__airtable_to_backend__
        }

        if hasattr(cls, "__field_translation_func__"):
            for key, func in cls.__field_translation_func__.items():
                if key in fields:
                    fields[key] = func(fields[key])

        for field in cls.__lookup_fields__:
            if field in fields.keys():
                if fields[field]:
                    fields[field] = fields[field][0]
                else:
                    fields[field] = None

        return cls(**{"airtable_id": id, **fields})

    def dict(self):
        return self.__dict__


def parse_date(airtable_date_str):
    return parser.parse(airtable_date_str) if airtable_date_str is not None else None


class Source(FromAirtable, StructuredNode):
    __airtable_to_backend__ = {
        "Label": "label",
        "Short label": "short_label",
        "Version": "version",
        "Description": "description",
    }
    airtable_id = StringProperty(unique_index=True, unique=True, required=True)
    label = StringProperty()
    short_label = StringProperty()
    version = StringProperty()
    description = StringProperty()


class Concept(FromAirtable, StructuredNode):
    __airtable_to_backend__ = {
        "Label": "label",
        "State": "state",
        "Code": "code",
        "Description": "description",
        "Created by": "created_by",
        "Created at": "created_at",
        "Updated by": "updated_by",
        "DBpedia ID": "dbpedia_id",
    }

    __field_translation_func__ = {
        "created_at": parse_date,
    }

    airtable_id = StringProperty(unique_index=True)
    dbpedia_id = StringProperty(unique_index=True)
    label = StringProperty()
    state = StringProperty()
    code = StringProperty()
    description = StringProperty()
    source = StringProperty()
    created_by = StringProperty()
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty()
    occurance = IntegerProperty()
    same_as = RelationshipTo("Concept", "SAMEAS")
    made_of = RelationshipTo("Concept", "MADEOF")
    parent_of = RelationshipTo("Concept", "PARENTOF")
    is_from = RelationshipTo("Source", "ISFROM")


class Company(Concept):
    pass


class Industry(Company):
    pass


class Product(Company):
    pass


class Impact(Concept):
    dbpedia_id = StringProperty(unique_index=True)
    has_category = RelationshipTo("ImpactCategory", "HASCATEGORY")
    subclass_of = RelationshipTo("Concept", "SUBCLASSOF")


class ImpactCategory(FromAirtable, StructuredNode):
    __airtable_to_backend__ = {
        "Label": "label",
        "State": "state",
        "Code": "code",
        "Description": "description",
        "Taxonomy": "source",
    }

    airtable_id = StringProperty(unique_index=True)
    label = StringProperty()
    state = StringProperty()
    description = StringProperty()
    is_from = RelationshipTo("Source", "ISFROM")  # taxonomy
    same_as = RelationshipTo("ImpactCategory", "SAMEAS")
    subclass_of = RelationshipTo("ImpactCategory", "SUBCLASSOF")


class ImpactTopic(StructuredNode):
    company_concept_label = StringProperty()
    impact_concept_label = StringProperty()
    company_concept_id = StringProperty()
    impact_concept_id = StringProperty()
    label = StringProperty()
    experiment = StringProperty()
    influenced_by = RelationshipFrom("Company", "INFLUENCES")
    influences = RelationshipTo("Impact", "INFLUENCES")
    polarity = StringProperty(
        choices={"POSITIVE": "Positive impact", "NEGATIVE": "Negative impact"}
    )
    occurance = IntegerProperty()
    improvement_levers = RelationshipTo("ImpactTopic", "CANIMPROVE")



