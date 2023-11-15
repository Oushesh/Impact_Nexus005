import unittest

from smart_evidence.helpers.classifier_util import (
    _results_to_predictions,
)


class TestConceptFilter(unittest.TestCase):
    def test_classifier(self):
        groups = {
            0: (
                {
                    "concept_label": "Fuels",
                    "label": "COMPANY",
                },
                {
                    "concept_label": "CO2",
                    "label": "IMPACT",
                },
            ),
            1: (
                {
                    "concept_label": "Fuels",
                    "label": "COMPANY",
                },
                {
                    "id": "Impact/IRIS/Waste/IMPACT;Waste",
                    "concept_label": "Waste",
                    "label": "IMPACT",
                },
            ),
            2: (
                {
                    "concept_label": "Fuels",
                    "label": "COMPANY",
                },
                {
                    "concept_label": "Energy efficiency",
                    "label": "IMPACT",
                },
            ),
            3: (
                {
                    "concept_label": "Fuels",
                    "label": "COMPANY",
                },
                {
                    "concept_label": "Air pollution",
                    "label": "IMPACT",
                },
            ),
            4: (
                {
                    "concept_label": "Natural gas",
                    "label": "COMPANY",
                },
                {
                    "concept_label": "CO2",
                    "label": "IMPACT",
                },
            ),
            5: (
                {
                    "concept_label": "Natural gas",
                    "label": "COMPANY",
                },
                {
                    "concept_label": "Air pollution",
                    "label": "IMPACT",
                },
            ),
        }

        results = {
            "sequence": "Emissions from the residential and commercial sectors declined by 19.5% and 13.7%, respectively. In relation to all CO 2 emissions from fuel combustion in 2014, oil was responsible for 61% of total emissions, while natural gas accounted for 25.7%, coal for 11.6%, and waste for the remaining 1.7%. Since 1990, CO 2 emissions from oil and coal have declined by 18.6% and 56.4%, respectively, while those from natural gas and waste were up by 37.8% and 123.7%. 1973 1976 1979 1982 1985 1988 1991 1994 1997 2000 2003 2006 7 1973 1976 1979 1982 1985 1988 1991 1994 1997 2000 2003 2006 2009 of public policy with the aim of protecting the environment, managing energy and sustainable development. An important part of ADEME's activities is dedicated to energy efficiency but also to climate, waste and air pollution.",
            "labels": [
                "Fuels has positive impact on the topic of CO2",
                "Fuels has negative impact on the topic of CO2",
                "Fuels does not have impact on the topic of CO2",
                "Fuels has positive impact on the topic of Waste",
                "Fuels has negative impact on the topic of Waste",
                "Fuels does not have impact on the topic of Waste",
                "Fuels has positive impact on the topic of Energy efficiency",
                "Fuels has negative impact on the topic of Energy efficiency",
                "Fuels does not have impact on the topic of Energy efficiency",
                "Fuels has positive impact on the topic of Air pollution",
                "Fuels has negative impact on the topic of Air pollution",
                "Fuels does not have impact on the topic of Air pollution",
                "Natural gas has positive impact on the topic of CO2",
                "Natural gas has negative impact on the topic of CO2",
                "Natural gas does not have impact on the topic of CO2",
                "Natural gas has positive impact on the topic of Air pollution",
                "Natural gas has negative impact on the topic of Air pollution",
                "Natural gas does not have impact on the topic of Air pollution",
            ],
            "scores": [
                # Fuel & CO2
                [0.1, 0.9],
                [0.6, 0.4],
                [0.0, 1.0],
                # Fuel & Waste
                [0.5, 0.5],
                [0.1, 0.9],
                [0.4, 0.6],
                # Fuel & Energy efficiency
                [0.6, 0.4],
                [0.4, 0.3],
                [0.1, 0.1],
                # Filters & Air pollution
                [0.5, 0.1],
                [0.2, 0.3],
                [0.3, 0.0],
                # Natural gas & CO2
                [0.6, 0.3],
                [0.7, 0.4],
                [0.1, 0.1],
                # Natural gas & Air pollution
                [0.6, 0.4],
                [0.2, 0.3],
                [0.1, 0.1],
            ],
            "groups": [
                0,
                0,
                0,
                1,
                1,
                1,
                2,
                2,
                2,
                3,
                3,
                3,
                4,
                4,
                4,
                5,
                5,
                5,
            ],
        }

        actual_output = _results_to_predictions(results, groups)
        self.assertEqual(
            [o["relation"] for o in actual_output],
            [
                "NOT_RELATED",
                "NEGATIVE",
                "POSITIVE_CONTRADICTION",
                "NEGATIVE",
                "NEGATIVE_CONTRADICTION",
                "POSITIVE_CONTRADICTION",
            ],
        )


if __name__ == "__main__":
    unittest.main()
