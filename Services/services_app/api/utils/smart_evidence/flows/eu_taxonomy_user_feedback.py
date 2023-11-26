from pathlib import Path
from typing import Dict, List
import typer
from pydantic import BaseModel, Extra

from app.models.annotation import (
    AnnotatedInsight,
    AnnotationType,
    ConceptAnnotation,
    InsightAnnotation,
    SimpleConcept,
)

from smart_evidence.flows.config_to_flow import get_flow, get_config
from smart_evidence.helpers.graphql import execute_graphql_query
from smart_evidence.components import Component
from smart_evidence.components.data_stores import (
    OpenSearchStore,
)
from smart_evidence.components.processors import ExtractScraperHTML, ParagraphProcessor


class EUTaxonomyClassificationFeedback(BaseModel):
    impact_goal_id: int
    venture_id: str = ""
    urls: List[str] = []

    class Config:
        # Forbid any extra fields in the request to avoid silent failures
        extra = Extra.forbid


def get_eu_taxonomy_user_feedback(
    config_path: Path = Path(
        "smart_evidence/flows/configs/eu_taxonomy_user_feedback.yaml"
    ),
):
    # setup pipeline and data store
    config: Dict = get_config(config_path=config_path)
    write_index: str = config.get("Pipeline").get("Config").get("write_index")  # type: ignore
    document_store = OpenSearchStore(
        component=Component(),
        component_config={
            "mode": "write",
            "index": write_index,
            "document_class": "AnnotatedInsight",
            "index_mapping": "INSIGHTS_MAPPING",
        },
    )

    ## fetch user feedbacks
    graphql_query: Dict = config.get("Pipeline").get("Config").get("graphql_query")  # type: ignore
    payload: Dict = {"query": graphql_query}
    impact_goals: List[Dict] = execute_graphql_query(payload=payload)["data"][
        "getImpactGoals"
    ]
    flow = eval(get_flow(config_path))  # pylint: disable=W0123
    user_feedback_insights: List[AnnotatedInsight] = []
    for impact_goal in impact_goals:
        try:
            ## aggregate content of each impact goal
            eu_taxonomy_feedback_item = EUTaxonomyClassificationFeedback(
                impact_goal_id=impact_goal["id"],
                venture_id=impact_goal["ventureId"],
                urls=impact_goal["activityUrls"],
            )
            documents: List[AnnotatedInsight] = flow.run(
                documents=eu_taxonomy_feedback_item
            )
            content: str = "\n\n\n".join([getattr(item, "text") for item in documents])
            urls: str = "\n\n\n".join(eu_taxonomy_feedback_item.urls)

            ## create annotation from each impact goal
            company_concepts: List[SimpleConcept] = [
                SimpleConcept(**business_activity)
                for business_activity in impact_goal["businessActivities"]
            ]

            annotation = InsightAnnotation(
                type=AnnotationType.machine,
                created_by=str(eu_taxonomy_feedback_item.venture_id),
            )
            annotation.tasks.concepts = ConceptAnnotation(
                company_concepts=company_concepts
            )
            aggregated_insight = AnnotatedInsight(
                id=str(eu_taxonomy_feedback_item.impact_goal_id),
                url=urls,
                text=content,
                venture_id=eu_taxonomy_feedback_item.venture_id,
                scraper="eu-taxonomy",
                par_index=0,
                document_id=str(eu_taxonomy_feedback_item.impact_goal_id),
                type="html",
                document_source="user_feedback",
                embedding=None,
                similarity_score=0.0,
                meta={},
            )
            aggregated_insight.add_annotation(annotation=annotation)
            user_feedback_insights.append(aggregated_insight)
        except Exception:
            continue

    ## write to data store
    document_store.run(documents=user_feedback_insights)
    print(
        f"Pipeline excecution has finished after processing {len(user_feedback_insights)} docs."
    )


if __name__ == "__main__":
    typer.run(get_eu_taxonomy_user_feedback)
