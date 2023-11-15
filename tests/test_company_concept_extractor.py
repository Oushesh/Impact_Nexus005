from app.models.annotation import AnnotatedInsight
from app.models.documents import DocumentType
from smart_evidence.components.base_component import Component
from smart_evidence.components.extractors.company_concept_extractor import (
    CompanyConceptExtractor,
)

num_of_keywords = 10

extractor = CompanyConceptExtractor(Component(), top_k=num_of_keywords)


document = AnnotatedInsight(
    id="",
    title="",
    url="",
    document_id="",
    scraper="",
    type=DocumentType.pdf,
    document_source="",
    par_index=0,
    highlight={},
    text="Globally CO2 emissions attributable to Information Technology are on par with those resulting from aviation. Recent growth in cloud service demand has elevated energy efficiency of data centers to a critical area within green computing. Cloud computing represents a backbone of IT services and recently there has been an increase in high-definition multimedia delivery, which has placed new burdens on energy resources. Hardware innovations together with energy-efficient techniques and algorithms are key to controlling power usage in an ever-expanding IT landscape. This special issue contains a number of contributions that show that data center energy efficiency should be addressed from diverse vantage points. Â© 2017 by the authors. Licensee MDPI, Basel, Switzerland.",
)
print(extractor.process(document))
