import unittest

from app.models.annotation import EntityAnnotation
from smart_evidence.components import Component
from smart_evidence.components.extractors import EntityLinker


class TestConceptClassifier(unittest.TestCase):
    input_items = [
        [
            {
                "text": "decent work",
                "id": "Decent_work",
                "concept_label": "Decent work",
                "label": "DBPEDIA_ENT",
                "start_token": 0,
                "end_token": 0,
                "start_char": 0,
                "end_char": 0,
            },
            {
                "text": "diversity",
                "id": "23",
                "concept_label": None,
                "label": "IMPACT",
                "start_token": 0,
                "end_token": 0,
                "start_char": 0,
                "end_char": 0,
            },
            {
                "text": "Building construction",
                "id": "Construction",
                "concept_label": "Construction",
                "label": "DBPEDIA_ENT",
                "start_token": 0,
                "end_token": 0,
                "start_char": 0,
                "end_char": 0,
            },
            {
                "text": "SDG indicator 6.b.1",
                "id": "sdg_6;SDG 6",
                "concept_label": "SDG 6",
                "label": "SDG",
                "start_token": 83,
                "end_token": 86,
                "start_char": 426,
                "end_char": 445,
            },
            {
                "text": "Chemical Manufacturing",
                "id": "10054",
                "concept_label": None,
                "label": "COMPANY",
                "start_token": 0,
                "end_token": 0,
                "start_char": 0,
                "end_char": 0,
            },
        ]
    ]
    expected_outputs = [
        {
            "company_concepts": [{"label": "Chemical Manufacturing", "id": "10054"}],
            "impact_concepts": [
                {"label": "Employment opportunities", "id": "26"},
                {"label": "Diversity", "id": "23"},
            ],
        }
    ]
    maxDiff = None

    def test_concept_classifier(self):
        entity_linker = EntityLinker(Component())
        for input_item, expected_output in zip(
            self.input_items,
            self.expected_outputs,
        ):
            concept_annotation = entity_linker(
                entities=EntityAnnotation.parse_obj(input_item)
            )
            print(concept_annotation.dict())
            self.assertEqual(concept_annotation.dict(), expected_output)


if __name__ == "__main__":
    unittest.main()
