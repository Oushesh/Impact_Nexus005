from typing import List, Optional, Tuple
import typer
import os
from haystack.document_stores import OpenSearchDocumentStore
from opensearchpy.helpers import scan
from app.models.annotation import InsightAnnotations
from smart_evidence.data_models.knowledgebase import Impact, Company, ImpactTopic
from smart_evidence.helpers import opensearch_connection
from smart_evidence.helpers.airtable_to_neo4j import write_concepts_airtable_to_neo4j
import pandas as pd
from py2neo.bulk import merge_nodes, merge_relationships
from py2neo import Graph

AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]
NEO4J_USER = os.environ["NEO4J_USER"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
NEO4J_URI = os.environ["NEO4J_URI"]

print(NEO4J_URI)
g = Graph("bolt://" + NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

BASE_QUERY = {
    "query": {
        "nested": {
            "path": "annotations.relations",
            "query": {
                "bool": {"must": [{"exists": {"field": "annotations.relations"}}]}
            },
        }
    }
}


LABEL_TRANSLATOR = {
    #     "POSITIVE_CONTRADICTION": "POSITIVE",
    #     "NEGATIVE_CONTRADICTION": "NEGATIVE",
    "POSITIVE": "POSITIVE",
    "NEGATIVE": "NEGATIVE",
}


def create_cooccurrence_matrix(insights, experiment_name):
    """Create co occurrence matrix from given list of annotated paragraphs.

    Returns:
    - company vocabs: dictionary of company concept counts
    - impact vocabs: dictionary of impact concept counts
    - co_occ_matrix_sparse: sparse co occurrence matrix

    Example:
    ===========
    vocabs,co_occ = create_cooccurrence_matrix(sentences)

    df_co_occ  = pd.DataFrame(co_occ.todense(),
                              index=vocabs.keys(),
                              columns = vocabs.keys())

    df_co_occ = df_co_occ.sort_index()[sorted(vocabs.keys())]

    df_co_occ.style.applymap(lambda x: 'color: red' if x>0 else '')

    """
    import scipy

    company_vocabulary = {}
    impact_vocabulary = {}
    data = []
    row = []
    col = []

    for insight in insights:
        annotations = InsightAnnotations(**insight["meta"]["annotations"])
        relation_ann = annotations.get_last_annotations(
            created_by=experiment_name
        ).relations
        if relation_ann is None:
            continue
        for sentence_prediction in relation_ann.annotation:
            if sentence_prediction.relation not in LABEL_TRANSLATOR.keys():
                continue

            label = LABEL_TRANSLATOR[sentence_prediction.relation]

            company_concept_id = sentence_prediction.company_concept.id
            company_concept_label = sentence_prediction.company_concept.label
            impact_concept_id = sentence_prediction.impact_concept.id
            impact_concept_label = sentence_prediction.impact_concept.label

            i = company_vocabulary.setdefault(
                (company_concept_id, company_concept_label, label),
                len(company_vocabulary),
            )
            j = impact_vocabulary.setdefault(
                (impact_concept_id, impact_concept_label), len(impact_vocabulary)
            )
            data.append(1)
            row.append(i)
            col.append(j)

    cooccurrence_matrix_sparse = scipy.sparse.coo_matrix((data, (row, col)))

    df = pd.DataFrame(
        cooccurrence_matrix_sparse.toarray(),
        index=company_vocabulary.keys(),
        columns=impact_vocabulary.keys(),
    )

    return df


def get_documents(index, created_by):
    # DocumentStore: holds all your data
    document_store = OpenSearchDocumentStore(
        username="admin",
        password="R9$Cix3vD$BU#z",
        host=opensearch_connection.HOST,
        port=443,
        timeout=60,
        aws4auth=opensearch_connection.AWS_AUTH,
        verify_certs=True,
        index=index,
        label_index="haystack-paragraphs-labels",
        search_fields=["text", "title"],
        similarity="cosine",
        content_field="text",
        name_field="title",
        analyzer="english",
        duplicate_documents="overwrite",
    )

    body = BASE_QUERY
    body["query"]["nested"]["query"]["bool"]["must"].append(
        {"term": {"annotations.relations.created_by": created_by}}
    )

    items = scan(
        document_store.client,
        query=body,
        index=index,
        size=1000,
        scroll="1h",
    )

    items = (
        document_store._convert_es_hit_to_document(
            item, return_embedding=False
        ).to_dict({"text": "content", "title": "name"})
        for item in items
    )
    return document_store, items


def get_impact_topics(df, experiment):
    for (company_concept_id, company_concept_label, polarity), row in df.iterrows():
        row = row[row > 0]
        row = row.dropna()

        for (impact_concept_id, impact_concept_label), count in row.iteritems():
            impact_topic = dict(
                label=f"",
                company_concept_label=company_concept_label,
                impact_concept_label=impact_concept_label,
                company_concept_id=company_concept_id,
                impact_concept_id=impact_concept_id,
                polarity=polarity,
                occurance=count,
                experiment=experiment,
            )
            yield impact_topic


def create_impact_topics(df, experiment_name):
    node_data = [
        dict(airtable_id=concept_id, label=concept_label, occurance=total_occurance)
        for (concept_id, concept_label), total_occurance in (
            df.sum(axis=1).groupby(level=[0, 1]).sum().iteritems()
        )
    ]
    merge_nodes(g.auto(), node_data, ("Company", "airtable_id", "label"))

    node_data = [
        dict(airtable_id=concept_id, label=concept_label, occurance=total_occurance)
        for (concept_id, concept_label), total_occurance in (df.sum(axis=0).iteritems())
    ]
    merge_nodes(g.auto(), node_data, ("Impact", "airtable_id", "label"))

    node_data = list(get_impact_topics(df, experiment_name))
    merge_nodes(
        g.auto(),
        node_data,
        ("ImpactTopic", "company_concept_id", "impact_concept_id", "polarity"),
    )

    relationship_data = [
        (node["company_concept_id"], {}, node["company_concept_id"])
        for node in node_data
    ]
    merge_relationships(
        g.auto(),
        relationship_data,
        "INFLUENCES",
        start_node_key=("Company", "airtable_id"),
        end_node_key=("ImpactTopic", "company_concept_id"),
    )

    relationship_data = [
        (node["impact_concept_id"], {}, node["impact_concept_id"]) for node in node_data
    ]
    merge_relationships(
        g.auto(),
        relationship_data,
        "INFLUENCES",
        start_node_key=("ImpactTopic", "impact_concept_id"),
        end_node_key=("Impact", "airtable_id"),
    )


def run_pipeline(index: str = "paragraphs", experiment: Optional[str] = None):
    """
    Writing relation extraction predictions to field `concept_predictions`
    """
    write_concepts_airtable_to_neo4j()
    _, insights = get_documents(index, experiment)
    df = create_cooccurrence_matrix(insights, experiment_name=experiment)
    print(df)
    create_impact_topics(df, experiment_name=experiment)


if __name__ == "__main__":
    typer.run(run_pipeline)
