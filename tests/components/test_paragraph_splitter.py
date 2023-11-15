import unittest
from app.models.documents import Document
from smart_evidence.components.processors import ParagraphProcessor
from smart_evidence.components import Component
from typing import List, Dict
from pathlib import Path
import os

from tests.utils.data_mocks import mock_document

"""
Configuration for default pipeline test
"""
input_items: List[Dict] = [
    {  ## no breaks
        "text": "The homes of the 20th century are much bigger than the homes of our family members from the 19th century, both in terms of square footage and number of rooms. Homes built at the beginning of the 21st century have 2-3 times more rooms than homes at the turn of the 20th century.",
        "type": "html",
    },
    {  ## single break
        "text": "The homes of the 20th century are much bigger than the homes of our family members. Drybrough's survived for several years and ceased brewing in January 1987\nThe homes of the 20th century are much bigger than the homes of our family members from the 19th century, both in terms of square footage and number of rooms. Homes built at the beginning of the 21st century have 2-3 times more rooms than homes at the turn of the 20th century.",
        "type": "pdf",
    },
    {  ## double breaks
        "text": "The late 19th and early 20th centuries saw seven breweries being built in what was open country at Craigmillar/Duddingston, concentrated in a small area beside the railway line and taking advantage of the local aquifers providing excellent water for brewing.\n\nThe first of these was the Craigmillar Brewery of William Murray & Co. Ltd built in 1886 and followed within a few years by Andrew Drybrough's brewery, also called the Craigmillar Brewery (1892), the Duddingston Brewery built by Pattisons Ltd (1896), bought by Robert Deuchar Ltd in 1899 following Pattisons' liquidation, the North British Brewery (1897) which was taken over by Murray's in 1927 becoming known as Murray's No. 2 Brewery, Maclauchlan's Castle Brewery, Raeburn's New Craigmillar Brewery and Paterson's Pentland Brewery, all opening in 1901., These breweries stopped brewing at various times, mainly in the 1960s, but Drybrough's survived for several years and ceased brewing in January 1987..",
        "type": "pdf",
    },
]


expected_items_single_break: List[Dict] = [
    {
        "text": "The homes of the 20th century are much bigger than the homes of our family members from the 19th century, both in terms of square footage and number of rooms. Homes built at the beginning of the 21st century have 2-3 times more rooms than homes at the turn of the 20th century.",
    },
    {
        "text": "The homes of the 20th century are much bigger than the homes of our family members. Drybrough's survived for several years and ceased brewing in January 1987",
    },
    {
        "text": "The homes of the 20th century are much bigger than the homes of our family members from the 19th century, both in terms of square footage and number of rooms. Homes built at the beginning of the 21st century have 2-3 times more rooms than homes at the turn of the 20th century.",
    },
    {
        "text": "The late 19th and early 20th centuries saw seven breweries being built in what was open country at Craigmillar/Duddingston, concentrated in a small area beside the railway line and taking advantage of the local aquifers providing excellent water for brewing.",
    },
    {
        "text": "The first of these was the Craigmillar Brewery of William Murray & Co. Ltd built in 1886 and followed within a few years by Andrew Drybrough's brewery, also called the Craigmillar Brewery (1892), the Duddingston Brewery built by Pattisons Ltd (1896), bought by Robert Deuchar Ltd in 1899 following Pattisons' liquidation, the North British Brewery (1897) which was taken over by Murray's in 1927 becoming known as Murray's No. 2 Brewery, Maclauchlan's Castle Brewery, Raeburn's New Craigmillar Brewery and Paterson's Pentland Brewery, all opening in 1901., These breweries stopped brewing at various times, mainly in the 1960s, but Drybrough's survived for several years and ceased brewing in January 1987..",
    },
]

expected_items_double_break: List[Dict] = [
    {
        "text": "The homes of the 20th century are much bigger than the homes of our family members from the 19th century, both in terms of square footage and number of rooms. Homes built at the beginning of the 21st century have 2-3 times more rooms than homes at the turn of the 20th century.",
    },
    {
        "text": "The homes of the 20th century are much bigger than the homes of our family members. Drybrough's survived for several years and ceased brewing in January 1987\nThe homes of the 20th century are much bigger than the homes of our family members from the 19th century, both in terms of square footage and number of rooms. Homes built at the beginning of the 21st century have 2-3 times more rooms than homes at the turn of the 20th century.",
    },
    {
        "text": "The late 19th and early 20th centuries saw seven breweries being built in what was open country at Craigmillar/Duddingston, concentrated in a small area beside the railway line and taking advantage of the local aquifers providing excellent water for brewing.",
    },
    {
        "text": "The first of these was the Craigmillar Brewery of William Murray & Co. Ltd built in 1886 and followed within a few years by Andrew Drybrough's brewery, also called the Craigmillar Brewery (1892), the Duddingston Brewery built by Pattisons Ltd (1896), bought by Robert Deuchar Ltd in 1899 following Pattisons' liquidation, the North British Brewery (1897) which was taken over by Murray's in 1927 becoming known as Murray's No. 2 Brewery, Maclauchlan's Castle Brewery, Raeburn's New Craigmillar Brewery and Paterson's Pentland Brewery, all opening in 1901., These breweries stopped brewing at various times, mainly in the 1960s, but Drybrough's survived for several years and ceased brewing in January 1987..",
    },
]

expected_items_fixed_strides: List[Dict] = [
    {
        "text": "The homes of the 20th century are much bigger than the homes of our family members from the 19th century, both in terms of square footage and number of rooms. Homes built at the beginning of the 21st century have 2-3 times more rooms than homes at the turn of the 20th century.",
    },
    {
        "text": "The homes of the 20th century are much bigger than the homes of our family members. Drybrough's survived for several years and ceased brewing in January 1987\nThe homes of the 20th century are much bigger than the homes of our family members from the 19th century, both in terms of square footage and number of rooms. Homes built at the beginning of the 21st century have 2-3 times more rooms than homes at the turn of the 20th century.",
    },
    {
        "text": "The late 19th and early 20th centuries saw seven breweries being built in what was open country at Craigmillar/Duddingston, concentrated in a small area beside the railway line and taking advantage of the local aquifers providing excellent water for brewing.\n\nThe first of these was the Craigmillar Brewery of William Murray & Co. Ltd built in 1886 and followed within a few years by Andrew Drybrough's brewery, also called the Craigmillar Brewery (1892), the Duddingston Brewery built by Pattisons Ltd (1896),"
    },
    {
        "text": "also called the Craigmillar Brewery (1892), the Duddingston Brewery built by Pattisons Ltd (1896), bought by Robert Deuchar Ltd in 1899 following Pattisons' liquidation, the North British Brewery (1897) which was taken over by Murray's in 1927 becoming known as Murray's No. 2 Brewery, Maclauchlan's Castle Brewery, Raeburn's New Craigmillar Brewery and Paterson's Pentland Brewery, all opening in 1901., These breweries stopped brewing at various times, mainly in the 1960s, but Drybrough's survived for several"
    },
    {
        "text": "breweries stopped brewing at various times, mainly in the 1960s, but Drybrough's survived for several years and ceased brewing in January 1987.."
    },
]

single_break_processor = ParagraphProcessor(
    Component(),
    component_config={"paragraph_marker": "single_break"},
    evaluation_config={},
)
double_break_processor = ParagraphProcessor(
    Component(),
    component_config={"paragraph_marker": "double_break"},
    evaluation_config={},
)
fixed_strides_processor = ParagraphProcessor(
    Component(),
    component_config={
        "paragraph_marker": "fixed_strides",
        "overlapping_strides": True,
        "split_stride_length": 100,
    },
    evaluation_config={},
)
document_type_processor = ParagraphProcessor(
    Component(),
    component_config={},
    evaluation_config={},
)


class TestParagraphSplitter(unittest.TestCase):
    def test_single_break_splitter(self):
        input_documents = [mock_document(document) for document in input_items]
        actual_output = single_break_processor.run(input_documents)
        for output, expected in zip(actual_output, expected_items_single_break):
            self.assertEqual(output.text, expected["text"])

    def test_double_break_splitter(self):
        input_documents = [mock_document(document) for document in input_items]
        actual_output = double_break_processor.run(input_documents)
        for output, expected in zip(actual_output, expected_items_double_break):
            self.assertEqual(output.text, expected["text"])

    def test_fixed_strides_splitter(self):
        input_documents = [mock_document(document) for document in input_items]
        actual_output = fixed_strides_processor.run(input_documents)
        for output, expected in zip(actual_output, expected_items_fixed_strides):
            self.assertEqual(output.text, expected["text"])

    def test_document_type_by_splitter(self):
        input_documents = [mock_document(document) for document in input_items]
        actual_output = document_type_processor.run(input_documents)
        for output, expected in zip(actual_output, expected_items_double_break):
            self.assertEqual(output.text, expected["text"])


if __name__ == "__main__":
    unittest.main()
