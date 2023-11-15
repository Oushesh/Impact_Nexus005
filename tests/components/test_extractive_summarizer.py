import unittest
from typing import List, Dict

from tests.utils.data_mocks import mock_document
from smart_evidence.components import Component
from smart_evidence.components.summarizers import ExtractiveSummarizer

"""
Configuration for default pipeline test
"""
input_items: List[Dict] = [
    {
        "text": "Countries\nThe Bitdal dam in Norway\nHydropower\nAt Statkraft, we have 125 years of experience in hydropower and are the largest producer of electricity from hydropower in Europe. The majority of our power production is hydropower.\nThe advantages of hydropower are many. It is renewable, clean, reliable, flexible and can serve many generations with low-cost electricity from local resources. Hydropower produces no air pollutants and shows the lowest Green House Gases (GHG) emission of all power generation technologies.\nIn Norway, 90 per cent of all power generation comes from hydropower. Worldwide, hydropower accounts for approximately one sixth of the total electricity supply.\nHydropower in numbers\n-\n347Number of hydropower plants\n-\n63 TWhTotal hydropower production\n-\n14,447 MWInstalled hydropower capacity\nEurope’s renewable energy battery\nThe Ringedal dam in Norway\nOur hydropower ambitions\nThe Nordic portfolio is a unique and important source of flexible and stable power. Given its age, we will continue with reinvestments to keep the portfolio competitive and profitable.\nWe are also focusing on optimising and protecting the value of our hydropower assets outside the Nordics and will pursue growth through selected acquisitions and swaps that fit well with the rest of the portfolio.\nRead more about our strategic ambitions\nHylen hydropower plant in Norway\nHow our hydropower plants work\nThe principle behind the production of hydropower is to use the energy of flowing water. Many hydropower plants benefit from several storage schemes. In some river systems we have several power stations positioned in cascade one after the other, so that the water’s energy can be exploited several times before it finally flows out into the sea. Inside the power station, the water drives a turbine producing mechanical energy which is turned into electrical energy in a generator. Hydropower schemes without reservoirs are often called run-of-river.\nHow our hydropower plants work\nVisit one of our power plants\nFind out more about our hydropower assets\nStatkraft has hydropower assets in Norway, Sweden, Germany, UK, Albania, Turkey, Brazil, Peru, Chile, Nepal and India. Find out more about our global hydropower activities by exploring the map below.",
    },
]

expected_items: List[Dict] = [
    {
        "text": "Countries\nThe Bitdal dam in Norway\nHydropower\nAt Statkraft, we have 125 years of experience in hydropower and are the largest producer of electricity from hydropower in Europe. The majority of our power production is hydropower.\nThe advantages of hydropower are many. It is renewable, clean, reliable, flexible and can serve many generations with low-cost electricity from local resources. Hydropower produces no air pollutants and shows the lowest Green House Gases (GHG) emission of all power generation technologies.\nIn Norway, 90 per cent of all power generation comes from hydropower. Worldwide, hydropower accounts for approximately one sixth of the total electricity supply.\nHydropower in numbers\n-\n347Number of hydropower plants\n-\n63 TWhTotal hydropower production\n-\n14,447 MWInstalled hydropower capacity\nEurope’s renewable energy battery\nThe Ringedal dam in Norway\nOur hydropower ambitions\nThe Nordic portfolio is a unique and important source of flexible and stable power. Given its age, we will continue with reinvestments to keep the portfolio competitive and profitable.\nWe are also focusing on optimising and protecting the value of our hydropower assets outside the Nordics and will pursue growth through selected acquisitions and swaps that fit well with the rest of the portfolio.\nRead more about our strategic ambitions\nHylen hydropower plant in Norway\nHow our hydropower plants work\nThe principle behind the production of hydropower is to use the energy of flowing water. Many hydropower plants benefit from several storage schemes. In some river systems we have several power stations positioned in cascade one after the other, so that the water’s energy can be exploited several times before it finally flows out into the sea. Inside the power station, the water drives a turbine producing mechanical energy which is turned into electrical energy in a generator. Hydropower schemes without reservoirs are often called run-of-river.\nHow our hydropower plants work\nVisit one of our power plants\nFind out more about our hydropower assets\nStatkraft has hydropower assets in Norway, Sweden, Germany, UK, Albania, Turkey, Brazil, Peru, Chile, Nepal and India. Find out more about our global hydropower activities by exploring the map below.",
        "summary": " At Statkraft, we are the largest producer of electricity from hydropower in Europe . 90 per cent of all power generation in Norway comes from hydroelectricity . The advantages of hydroelectricity are many: it is renewable, clean, reliable, flexible and can serve many generations with low-cost electricity from local resources .",
    },
]

pipeline = ExtractiveSummarizer(
    Component(),
    component_config={
        "model_name_or_path": "sshleifer/distilbart-cnn-12-6",
        "summary_min_length": 5,
        "summary_max_length": 100,
    },
    evaluation_config={},
)


class TestExtractiveSummarizer(unittest.TestCase):
    def test_extractive_summarizer(self):
        input_documents = [mock_document(document) for document in input_items]
        actual_output = pipeline.run(input_documents)
        for output, expected in zip(actual_output, expected_items):
            self.assertEqual(output.summary, expected["summary"])


if __name__ == "__main__":
    unittest.main()
