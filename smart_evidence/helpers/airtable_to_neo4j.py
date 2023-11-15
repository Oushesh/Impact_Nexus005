"""
Writes airtable data to neo4j
"""
from collections import defaultdict
import logging
import os
from typing import Dict, List, Tuple
import typer
from pyairtable import Table
from smart_evidence.models.knowledgebase import (
    ImpactCategory,
    Source,
)
from collections import Counter
from dotenv import load_dotenv
from py2neo import Graph
from py2neo.bulk import merge_nodes, merge_relationships


NEO4J_USER = os.environ["NEO4J_USER"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
NEO4J_URI = os.environ["NEO4J_URI"]

g = Graph("bolt://" + NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

load_dotenv()

logging.basicConfig(level=logging.INFO)


AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]


def write_sources_to_neo4j(sources: list = []):
    sources_fields = [
        Source.from_airtable(**record).dict()
        for record in records
        if record["fields"]["Label"]
    ]
    Source.create_or_update(*sources_fields)
    logging.info(f"{len(sources_fields)} Sources nodes recorded")


def write_company_concepts_to_neo4j(company_concepts: list):
    concepts_fields: Dict[tuple, List] = defaultdict(lambda: list())
    other_labels = ("Concept",)

    for concept in company_concepts:
        node = CompanyConcept.from_airtable(**concept)
        node_labels = tuple(sorted(concept["fields"].get("Type", [])))
        airtable_fields = node.dict()
        airtable_fields["airtable_id"] = airtable_fields.pop("id")
        airtable_fields.pop("type")
        concepts_fields[node_labels].append(airtable_fields)

    print(Counter({k: len(v) for k, v in concepts_fields.items()}))
    n_company_concepts = 0
    n_relationships = 0
    for labels, nodes in concepts_fields.items():
        node_data = [{k: v for k, v in node.items() if k != "source"} for node in nodes]
        relationship_data: List[Tuple] = []
        for node in nodes:
            sources = node.get("source")
            if sources:
                for source in sources:
                    relationship_data.append((node["airtable_id"], {}, source))

        n_company_concepts += len(node_data)
        n_relationships += len(relationship_data)
        merge_nodes(
            g.auto(),
            node_data,
            ("Company", "airtable_id"),
            labels=labels + other_labels,
        )

        merge_relationships(
            g.auto(),
            relationship_data,
            "ISFROM",
            start_node_key=("Company", "airtable_id"),
            end_node_key=("Source", "airtable_id"),
        )

    logging.info(
        f"{n_company_concepts} Company nodes with {n_relationships} source relationships are recorded"
    )


def write_impact_concepts_to_neo4j(impact_concepts):
    other_labels = ("Concept",)
    node_data = []
    relationship_data: List[Tuple] = []
    for concept in impact_concepts:
        node = ImpactConcept.from_airtable(**concept)
        airtable_fields = node.dict()
        airtable_fields["airtable_id"] = airtable_fields.pop("id")
        if airtable_fields.get("source"):
            for source in airtable_fields.get("source"):
                relationship_data.append((airtable_fields["airtable_id"], {}, source))
            airtable_fields.pop("source")
        node_data.append(airtable_fields)
    merge_nodes(g.auto(), node_data, ("Impact", "airtable_id"), labels=other_labels)
    merge_relationships(
        g.auto(),
        relationship_data,
        "ISFROM",
        start_node_key=("Impact", "airtable_id"),
        end_node_key=("Source", "airtable_id"),
    )
    logging.info(f"{len(node_data)} Impact nodes recorded")


def write_impact_categories_to_neo4j(impact_categories):
    impact_categories_fields = []
    relationship_data: List[Tuple] = []
    for record in impact_categories:
        if record["fields"]["Label"]:
            impact_categories_fields.append(
                ImpactCategory.from_airtable(**record).dict()
            )
            sources = record["fields"].get("Taxonomy")
            if sources:
                for source in sources:
                    relationship_data.append((record["id"], {}, source))

    ImpactCategory.create_or_update(*impact_categories_fields)
    merge_relationships(
        g.auto(),
        relationship_data,
        "ISFROM",
        start_node_key=("ImpactCategory", "airtable_id"),
        end_node_key=("Source", "airtable_id"),
    )

    logging.info(f"{len(impact_categories_fields)} ImpactCategory nodes recorded")


def create_company_concepts_rels_neo4j(company_concepts):
    n_relations = 0
    parentof_relationship_data: List[Tuple] = []
    for concept in company_concepts:
        airtable_id = concept["id"]
        # PARENTOF
        peers = concept["fields"].get("PARENTOF")
        if peers is not None:
            for peer in peers:
                parentof_relationship_data.append((airtable_id, {}, peer))
                n_relations += 1

    merge_relationships(
        g.auto(),
        parentof_relationship_data,
        "PARENTOF",
        start_node_key=("Concept", "airtable_id"),
        end_node_key=("Concept", "airtable_id"),
    )

    logging.info(f"{n_relations} CompanyConcept relations recorded")


def create_impact_concepts_rels_neo4j(impact_concepts):
    n_relations = 0
    subclassesof_relationship_data: List[Tuple] = []
    sameas_relationship_data: List[Tuple] = []
    has_category_relationship_data: List[Tuple] = []
    for concept in impact_concepts:
        airtable_id = concept["id"]
        # SUBCLASSOF
        peers = concept["fields"].get("SUBCLASSOF")
        if peers is not None:
            for peer in peers:
                subclassesof_relationship_data.append((airtable_id, {}, peer))
                n_relations += 1
        # SAMEAS
        peers = concept["fields"].get("SAMEAS")
        if peers is not None:
            for peer in peers:
                sameas_relationship_data.append((airtable_id, {}, peer))
                n_relations += 1
        # HASCATEGORY
        peers = concept["fields"].get("CATEGORY")
        if peers is not None:
            for peer in peers:
                has_category_relationship_data.append((airtable_id, {}, peer))
                n_relations += 1

    merge_relationships(
        g.auto(),
        subclassesof_relationship_data,
        "SUBCLASSOF",
        start_node_key=("Concept", "airtable_id"),
        end_node_key=("Concept", "airtable_id"),
    )
    merge_relationships(
        g.auto(),
        sameas_relationship_data,
        "SAMEAS",
        start_node_key=("Concept", "airtable_id"),
        end_node_key=("Concept", "airtable_id"),
    )
    merge_relationships(
        g.auto(),
        has_category_relationship_data,
        "HASCATEGORY",
        start_node_key=("Concept", "airtable_id"),
        end_node_key=("ImpactCategory", "airtable_id"),
    )
    logging.info(f"{n_relations} Impact relations recorded")


def create_impact_category_rels_neo4j(impact_categories):
    n_relations = 0
    subclassesof_relationship_data: List[Tuple] = []
    sameas_relationship_data: List[Tuple] = []
    for concept in impact_categories:
        # SUBCLASSOF
        airtable_id = concept["id"]
        peers = concept["fields"].get("SUBCLASSOF")
        if peers is not None:
            for peer in peers:
                subclassesof_relationship_data.append((airtable_id, {}, peer))
                n_relations += 1
        # SAMEAS
        peers = concept["fields"].get("SAMEAS")
        if peers is not None:
            for peer in peers:
                sameas_relationship_data.append((airtable_id, {}, peer))
                n_relations += 1

    merge_relationships(
        g.auto(),
        subclassesof_relationship_data,
        "SUBCLASSOF",
        start_node_key=("ImpactCategory", "airtable_id"),
        end_node_key=("ImpactCategory", "airtable_id"),
    )
    merge_relationships(
        g.auto(),
        sameas_relationship_data,
        "SAMEAS",
        start_node_key=("ImpactCategory", "airtable_id"),
        end_node_key=("ImpactCategory", "airtable_id"),
    )
    logging.info(f"{n_relations} ImpactCategory relations recorded")


def write_concepts_airtable_to_neo4j(
    sources_airtable_table_name: str = "Source",
    company_concepts_airtable_table_name: str = "CompanyConcept",
    impact_categories_airtable_table_name: str = "ImpactCategory",
    impact_concepts_airtable_table_name: str = "ImpactConcept",
):
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, sources_airtable_table_name)
    sources = table.all()

    table = Table(
        AIRTABLE_API_KEY, AIRTABLE_BASE_ID, company_concepts_airtable_table_name
    )
    company_concepts = table.all()

    table = Table(
        AIRTABLE_API_KEY, AIRTABLE_BASE_ID, impact_categories_airtable_table_name
    )
    impact_categories = table.all()

    table = Table(
        AIRTABLE_API_KEY, AIRTABLE_BASE_ID, impact_concepts_airtable_table_name
    )
    impact_concepts = table.all()

    write_sources_to_neo4j(sources)
    write_company_concepts_to_neo4j(company_concepts)
    write_impact_concepts_to_neo4j(impact_concepts)
    write_impact_categories_to_neo4j(impact_categories)
    create_company_concepts_rels_neo4j(company_concepts)
    create_impact_concepts_rels_neo4j(impact_concepts)
    create_impact_category_rels_neo4j(impact_categories)


if __name__ == "__main__":
    typer.run(write_concepts_airtable_to_neo4j)
