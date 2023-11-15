import unittest
from app.models.annotation import AnnotatedInsight
from smart_evidence.components.filters import (
    DateFilter,
    LanguageFilter,
    RelevancyFilter,
    InsightFilter,
)
from smart_evidence.components import Component
from typing import List, Dict
from pathlib import Path
import os

from tests.utils.data_mocks import mock_insight

"""
Configuration for default pipeline test
"""
input_items: List[Dict] = [
    {
        "text": "Hallo Welt",
    },
    {
        "text": "The homes of the 20th century are much bigger than the homes of our family members",
    },
    {
        "text": "The late 19th and early 20th centuries saw seven breweries being built in what was open country at Craigmillar/Duddingston, concentrated in a small area beside the railway line and taking advantage of the local aquifers providing excellent water for brewing., The first of these was the Craigmillar Brewery of William Murray & Co. Ltd built in 1886 and followed within a few years by Andrew Drybrough's brewery, also called the Craigmillar Brewery (1892), the Duddingston Brewery built by Pattisons Ltd (1896), bought by Robert Deuchar Ltd in 1899 following Pattisons' liquidation, the North British Brewery (1897) which was taken over by Murray's in 1927 becoming known as Murray's No. 2 Brewery, Maclauchlan's Castle Brewery, Raeburn's New Craigmillar Brewery and Paterson's Pentland Brewery, all opening in 1901., These breweries stopped brewing at various times, mainly in the 1960s, but Drybrough's survived for several years and ceased brewing in January 1987..",
    },
    {
        "text": "The homes of the 20th century are much bigger than the homes of our family members from the 19th century, both in terms of square footage and number of rooms. Homes built at the beginning of the 21st century have 2-3 times more rooms than homes at the turn of the 20th century.",
    },
    {
        "text": "<p>Abbreviations: SE, standard error; CI, confidence interval.<\/p>\u00a7<p>Two-tailed two independent samples Student\u2019s <i>t<\/i>-test for difference in seasonal amplitudes.<\/p>\u00b6<p>Student-Newman-Keuls Method of one way analysis of variance for all pairwise multiple comparison among seasonal amplitudes.<\/p>\u2020<p><i>P<\/i> value>0.05 for difference in seasonal amplitudes between subgroup of peasant and subgroup of migrant worker.<\/p",
    },
]


expected_items: List[Dict] = [
    {
        "text": "The homes of the 20th century are much bigger than the homes of our family members from the 19th century, both in terms of square footage and number of rooms. Homes built at the beginning of the 21st century have 2-3 times more rooms than homes at the turn of the 20th century.",
    },
]

filters_pipeline = DateFilter(
    LanguageFilter(
        RelevancyFilter(
            InsightFilter(
                Component(),
                component_config={
                    "model_name_or_path": "models/insights_classifier_v1/"
                },
            )
        )
    )
)


class TestConceptFilter(unittest.TestCase):
    def test_paragraph_filter(self):
        input_insights = [mock_insight(**insight) for insight in input_items]
        actual_output = filters_pipeline.run(input_insights)
        for output, expected in zip(actual_output, expected_items):
            self.assertEqual(output.text, expected["text"])
            self.assertEqual(output.annotations[0].tasks.content_control, "FEATURED")


if __name__ == "__main__":
    unittest.main()
