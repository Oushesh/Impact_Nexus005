import unittest

from app.models.annotation import ConceptAnnotation
from smart_evidence.components import Component
from smart_evidence.components.classifiers import (
    CompanyImpactClassifier,
    BoolQACompanyImpactClassifier,
)


class TestConceptClassifier(unittest.TestCase):
    input_items = [
        {
            "text": "Residential building construction is important for providing affordable housing.",
            "concepts": {
                "company_concepts": [
                    {
                        "label": "Residential Building Construction",
                        "id": "10408",
                    }
                ],
                "impact_concepts": [
                    {
                        "id": "14",
                        "label": "Housing",
                    }
                ],
            },
        },
    ]
    expected_outputs = [
        [
            {
                "company_concept": {
                    "label": "Residential Building Construction",
                    "id": "10408",
                },
                "impact_concept": {
                    "id": "14",
                    "label": "Housing",
                },
                "relation": "POSITIVE",
            },
        ]
    ]
    maxDiff = None

    def test_company_impact_classifier(self):
        concept_classifier = CompanyImpactClassifier(Component())
        for input_item, expected_output in zip(
            self.input_items,
            self.expected_outputs,
        ):
            actual_output = concept_classifier(
                input_item["text"],
                ConceptAnnotation(**input_item["concepts"]),
            )
            actual_output = actual_output.dict()["__root__"]
            del actual_output[0]["logit"]
            self.assertEqual(actual_output, expected_output)

    def test_boolqa_concept_classifier(self):
        concept_classifier = BoolQACompanyImpactClassifier(
            Component(),
            component_config={
                "model_name_or_path": "models/boolqa_concept_relation_classifier"
            },
        )
        for input_item, expected_output in zip(
            self.input_items,
            self.expected_outputs,
        ):
            actual_output = concept_classifier(
                input_item["text"],
                ConceptAnnotation(**input_item["concepts"]),
            )
            actual_output = actual_output.dict()["__root__"]
            del actual_output[0]["logit"]
            self.assertEqual(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main()
