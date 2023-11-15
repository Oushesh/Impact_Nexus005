import unittest
from typing import List, Dict

from tests.utils.data_mocks import mock_insight
from smart_evidence.components import Component
from smart_evidence.components.processors import AggregateContent

"""
Configuration for default pipeline test
"""
input_items: List[Dict] = [
    {
        "text": "The homes of the 20th century are much bigger than the homes of our family members",
        "title": "homes of the 20th century",
    },
]

expected_items: List[Dict] = [
    {
        "text": "homes of the 20th century \t The homes of the 20th century are much bigger than the homes of our family members",
        "title": "homes of the 20th century",
    },
]

pipeline = AggregateContent(
    Component(),
    component_config={
        "aggregation_fields": ["title", "text"],
        "aggregation_delimeter": " \t ",
    },
    evaluation_config={},
)


class TestAggregateContent(unittest.TestCase):
    def test_paragraph_filter(self):
        input_insights = [mock_insight(insight) for insight in input_items]
        actual_output = pipeline.run(input_insights)
        for output, expected in zip(actual_output, expected_items):
            self.assertEqual(output.text, expected["text"])


if __name__ == "__main__":
    unittest.main()
