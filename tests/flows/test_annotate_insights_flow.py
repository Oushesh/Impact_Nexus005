import unittest
from pathlib import Path

from smart_evidence.components import Component
from smart_evidence.components.classifiers import CompanyImpactClassifier
from smart_evidence.components.extractors import EntityExtractor, EntityLinker
from smart_evidence.flows.config_to_flow import get_flow
from tests.utils.data_mocks import mock_insight


class TestConceptClassifier(unittest.TestCase):
    input_items = [
        {
            "text": "Residential building construction is important for providing affordable housing.",
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

    def test_annotate_flow(self):
        config_path = Path("tests/flows/configs/test_annotate_insights.yaml")
        flow = eval(get_flow(config_path))
        for input_item, expected_output in zip(
            self.input_items,
            self.expected_outputs,
        ):
            document = mock_insight(**input_item)

            documents = flow.run([document])
            document = documents[0]

            annotation = document.get_annotation_by(flow.config["experiment_name"])
            assert annotation is not None
            actual_output = annotation.tasks.relations.dict()["__root__"]

            for o in actual_output:
                del o["logit"]

            self.assertEqual(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main()
