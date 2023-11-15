import logging
from typing import Any, Dict, List
from app.models.annotation import (
    AnnotatedInsight,
    AnnotationType,
    ConceptAnnotation,
    InsightAnnotation,
    SimpleConcept,
)
from app.models.concepts import ConceptML
from smart_evidence.components import BaseComponent
from smart_evidence.components.classifiers.zero_shot_classifier import (
    ZeroShotClassifier,
)
from smart_evidence.components import Component
from smart_evidence.components.data_stores import OpenSearchStore
from smart_evidence.flows.config_to_flow import get_flow
import pandas as pd
from tqdm import tqdm
from enum import Enum
import json

logger = logging.getLogger(__name__)

class PredictionType(str, Enum):
    sector = "sector"
    activity = "activity"

class ConceptFilter(str, Enum):
    dense_concept_retriever = "dense_concept_retriever"
    sector_classifier = "sector_classifier"
    mediod_concept_clustering = "mediod_concept_clustering"

class EUTaxonomyClassifier(ZeroShotClassifier):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        self.argmax_prediction = self.component_config.get("argmax_prediction", False)
        eu_taxonomy_file_url = self.component_config.get("eu_taxonomy_file_url", "")
        self.eu_taxonomy_df = pd.read_excel(eu_taxonomy_file_url)
        self.concept_filter_type = self.component_config.get("concept_filter_type")
        self.classification_threshold = self.component_config.get(
            "classification_threshold", 0.0
        )  # returns all predictions by default
        assert (
            self.concept_filter_type is not None
        ), "Please specify the concept filter type to execute EU Taxonomy classifier"

        # config for dense concept store retriever
        if self.concept_filter_type == ConceptFilter.dense_concept_retriever:
            assert len(
                self.component_config.get("concept_datastore", {})
            ), "Concept Store for EU Taxonomy classifier incorrectly configured"
            self.concept_datastore = eval(
                get_flow(
                    self.component_config.get("concept_datastore", {}), is_file=False
                )
            )
            self.top_k = self.component_config.get("top_k", 5)
            self.filters = self.concept_datastore.component_config.get("filters", {})

        elif self.concept_filter_type == ConceptFilter.mediod_concept_clustering:
            with open(
                self.component_config.get(
                    "medoid_clustering_meta_path",
                    "models/eu_taxonomy_medoid_clustering_meta.json",
                ),
                "r",
            ) as meta_file:
                self._medoid_clustering_meta = json.load(meta_file)

    def process(self, document: AnnotatedInsight, **kwds) -> Any:
        labels: List = kwds.get("labels", [])
        prediction_type: PredictionType = kwds.get("prediction_type")  # type: ignore
        prediction: Dict = self.pipeline(
            getattr(document, self.content_field), candidate_labels=labels  # type: ignore
        )
        if "scores" in prediction:
            for score, concept in zip(prediction["scores"], prediction["labels"]):
                if prediction_type == PredictionType.sector:
                    return concept
                elif (
                    prediction_type == PredictionType.activity
                    and score >= self.classification_threshold
                ):
                    annotation = document.get_annotation_by(
                        self.config.get("experiment_name", "test_experiment")
                    )

                    if annotation is None:
                        annotation = InsightAnnotation(
                            type=AnnotationType.machine,
                            created_by=self.config.get(
                                "experiment_name", "test_experiment"
                            ),
                        )

                    company_concepts = [SimpleConcept(label=concept, id="-1")]
                    if annotation.tasks.concepts is None:
                        annotation.tasks.concepts = ConceptAnnotation(
                            company_concepts=company_concepts
                        )
                    else:
                        for concept in company_concepts:
                            if (
                                concept
                                not in annotation.tasks.concepts.company_concepts
                            ):
                                annotation.tasks.concepts.company_concepts.append(
                                    concept
                                )

                    document.add_annotation(annotation)  # type: ignore
                    # only add highest posterior prediction as annotation
                    if self.argmax_prediction:
                        return document
                else:
                    # stop processing rest of the posteriors which are below threshold
                    break

        return document

    def run(
        self,
        documents: List[AnnotatedInsight],
        **kwds,
    ) -> List[AnnotatedInsight]:
        assert "Sector" in list(self.eu_taxonomy_df.columns) and "Activity" in list(
            self.eu_taxonomy_df.columns
        ), "Sector and Activity must be present in EU Taxonomy file for classification"

        sectors = list(set(self.eu_taxonomy_df.Sector))
        processed_documents = []
        for document in tqdm(documents):
            activities = []
            if self.concept_filter_type == ConceptFilter.dense_concept_retriever:
                activity_concepts = self.concept_datastore.query_by_embedding(
                    query_emb=document.embedding, filters=self.filters, top_k=self.top_k
                )
                activities = [
                    activity_concept.label for activity_concept in activity_concepts
                ]
            elif self.concept_filter_type == ConceptFilter.sector_classifier:
                sector = self.process(
                    document, labels=sectors, prediction_type=PredictionType.sector
                )

                # filter activities by sector
                activities = list(
                    set(
                        self.eu_taxonomy_df[
                            self.eu_taxonomy_df.Sector == sector
                        ].Activity
                    )
                )

            elif self.concept_filter_type == ConceptFilter.mediod_concept_clustering:
                mediod_activity = self.process(
                    document,
                    labels=self._medoid_clustering_meta["medoid_activities"],
                    prediction_type=PredictionType.sector,
                )
                index_of_medoid: int = self._medoid_clustering_meta["activities"].index(
                    mediod_activity
                )
                # filter activities based on cluster mediod
                activities = [
                    self._medoid_clustering_meta["activities"][idx]
                    for idx, medoid_idx in enumerate(
                        self._medoid_clustering_meta["activity_medoids"]
                    )
                    if (medoid_idx == index_of_medoid)
                ]

            processed_document = self.process(
                document, labels=activities, prediction_type=PredictionType.activity
            )

            if processed_document is not None:
                processed_documents.append(processed_document)

        return self.component.run(processed_documents, **kwds)
