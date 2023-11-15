import unittest

from smart_evidence.components import Component
from smart_evidence.components.classifiers import CompanyImpactClassifier
from smart_evidence.components.extractors import EntityExtractor, EntityLinker
from tests.utils.data_mocks import mock_insight


class TestConceptClassifier(unittest.TestCase):
    input_items = [
        {
            "text": "Residential building construction is important for providing affordable housing",
        }
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

    def test_annotate_flow_components(self):
        experiment_name = "test"
        entity_extractor = EntityExtractor(
            Component(), config={"experiment_name": experiment_name}
        )
        entity_linker = EntityLinker(
            Component(), config={"experiment_name": experiment_name}
        )
        concept_classifier = CompanyImpactClassifier(
            Component(), config={"experiment_name": experiment_name}
        )
        for input_item, expected_output in zip(
            self.input_items,
            self.expected_outputs,
        ):
            document = mock_insight(input_item["text"])

            document = entity_extractor.process(document)
            document = entity_linker.process(document)
            assert document is not None
            document = concept_classifier.process(document)
            assert document is not None
            annotation = document.get_annotation_by(experiment_name)
            assert annotation is not None
            actual_output = annotation.tasks.relations.dict()["__root__"]

            for o in actual_output:
                del o["logit"]

            self.assertEqual(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main()
