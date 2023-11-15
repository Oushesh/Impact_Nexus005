import unittest
from smart_evidence.components.base_component import Component

from smart_evidence.components.extractors import EntityExtractor


class TestAnnotationGenerator(unittest.TestCase):

    input_items = [
        {
            "text": "There is broad use of the Sustainable Development Goals (SDGs) with 73% using this framework for at least one measurement and management purpose. Nearly threequarters of respondents to this year' s survey target ' decent work and economic growth' (SDG 8). On average, respondents target eight different SDG-aligned impact themes, reflecting the diversity of their impact goals. // We want to label SDG goal 9, SDG target 4.9, SDG indicator 6.b.1 as well as goal 9, target 4.9, indicator 17.19.2, but not SDG 2021.",
        }
    ]

    expected_output_defs = [
        [
            {
                "text": "SDGs",
                "id": "sdg;SDG",
                "concept_label": "SDG",
                "label": "SDG",
                "start_token": 10,
                "end_token": 11,
                "start_char": 57,
                "end_char": 61,
            },
            {
                "text": "SDG target 4.9",
                "id": "sdg_4;SDG 4",
                "concept_label": "SDG 4",
                "label": "SDG",
                "start_token": 79,
                "end_token": 82,
                "start_char": 410,
                "end_char": 424,
            },
            {
                "text": "Sustainable Development Goals",
                "id": "sdg;SDG",
                "concept_label": "SDG",
                "label": "SDG",
                "start_token": 6,
                "end_token": 9,
                "start_char": 26,
                "end_char": 55,
            },
            {
                "text": "SDG 8)",
                "id": "sdg_8;SDG 8",
                "concept_label": "SDG 8",
                "label": "SDG",
                "start_token": 46,
                "end_token": 48,
                "start_char": 248,
                "end_char": 254,
            },
            {
                "text": "SDG",
                "id": "sdg;SDG",
                "concept_label": "SDG",
                "label": "SDG",
                "start_token": 56,
                "end_token": 57,
                "start_char": 303,
                "end_char": 306,
            },
            {
                "text": "target 4.9",
                "id": "sdg_4;SDG 4",
                "concept_label": "SDG 4",
                "label": "SDG",
                "start_token": 92,
                "end_token": 94,
                "start_char": 465,
                "end_char": 475,
            },
            {
                "text": "SDG",
                "id": "sdg;SDG",
                "concept_label": "SDG",
                "label": "SDG",
                "start_token": 100,
                "end_token": 101,
                "start_char": 504,
                "end_char": 507,
            },
            {
                "text": "SDG goal 9",
                "id": "sdg_9;SDG 9",
                "concept_label": "SDG 9",
                "label": "SDG",
                "start_token": 75,
                "end_token": 78,
                "start_char": 398,
                "end_char": 408,
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
                "text": "goal 9",
                "id": "sdg_9;SDG 9",
                "concept_label": "SDG 9",
                "label": "SDG",
                "start_token": 89,
                "end_token": 91,
                "start_char": 457,
                "end_char": 463,
            },
            {
                "text": "indicator 17.19.2",
                "id": "sdg_17;SDG 17",
                "concept_label": "SDG 17",
                "label": "SDG",
                "start_token": 95,
                "end_token": 97,
                "start_char": 477,
                "end_char": 494,
            },
        ]
    ]

    def test_annotations(self):
        entity_extractor = EntityExtractor(Component())
        for input_item, expected_output in zip(
            self.input_items, self.expected_output_defs
        ):
            actual_output = entity_extractor(input_item["text"])
            output_entity_list = actual_output.dict()["__root__"]

            for expected_entity in expected_output:
                self.assertIn(expected_entity, output_entity_list)
