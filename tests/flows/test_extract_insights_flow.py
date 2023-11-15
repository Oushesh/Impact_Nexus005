from pathlib import Path
import unittest
from app.models.documents import Document
from app.models.impact_screening import Insight

from smart_evidence.components.processors.paragraph_processor import ParagraphProcessor
from smart_evidence.components import Component
from smart_evidence.flows.config_to_flow import get_flow
from tests.utils.data_mocks import mock_insight


class TestConceptClassifier(unittest.TestCase):
    input_items = [
        {
            "id": "abc",
            "url": "https://abc.com/text",
            "uri": "",
            "storage_url": "",
            "type": "pdf",
            "scraper": "test",
            "text": "The buildings and construction sector accounted for 36% of final energy use and 39% of energy and process-related carbon dioxide (CO2) emissions in 2018, 11% of which resulted from manufacturing building materials and products such as steel, cement and glass.\n\nContents -----------------------------------------------------------------------------------------------------------------------------------------------------\n\nThis is an extract, full report available as PDF download\n\nTowardsazero-emissions,efficientandresilientbuildingsandconstructionsector\n\nThis year’s Global Status Report for Buildings and Construction provides an update on drivers of CO2 emissions and energy demand globally from 2017, along with examples of policies, technologies and investments that support low-carbon building stocks.",
        }
    ]
    expected_outputs = [
        [
            {
                "id": "205061d77ac696afaf017168a54b2108",
                "title": None,
                "url": "https://abc.com/text",
                "text": "The buildings and construction sector accounted for 36% of final energy use and 39% of energy and process-related carbon dioxide (CO2) emissions in 2018, 11% of which resulted from manufacturing building materials and products such as steel, cement and glass.",
                "document_id": "abc",
                "scraper": "test",
                "type": "pdf",
                "par_index": 0,
                "highlight": None,
                "document_source": None,
                "meta": None,
                "content_type": "text",
            },
            {
                "id": "4ed2a180282f390a81d9af42e35a5dbd",
                "title": None,
                "url": "https://abc.com/text",
                "text": "This year’s Global Status Report for Buildings and Construction provides an update on drivers of CO2 emissions and energy demand globally from 2017, along with examples of policies, technologies and investments that support low-carbon building stocks.",
                "document_id": "abc",
                "scraper": "test",
                "type": "pdf",
                "par_index": 4,
                "highlight": None,
                "document_source": None,
                "meta": None,
                "content_type": "text",
            },
        ]
    ]
    maxDiff = None

    def test_extract_insights_flow(self):
        config_path = Path("tests/flows/configs/test_extract_insights.yaml")
        flow = eval(get_flow(config_path))
        for input_item, expected_output in zip(
            self.input_items,
            self.expected_outputs,
        ):

            insights = flow.run([Document(**input_item)])
            for insight, expected_insight in zip(insights, expected_output):
                self.assertDictContainsSubset(expected_insight, insight.dict())


if __name__ == "__main__":
    unittest.main()
