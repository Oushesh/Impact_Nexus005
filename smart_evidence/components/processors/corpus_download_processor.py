from pathlib import Path
from typing import List, Any

import boto3
import srsly
import typer
from tqdm import tqdm
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Attr, AttributeExists
from smart_evidence.components import BaseComponent
from smart_evidence.components.processors.base_processor import BaseProcessor

load_dotenv()


class CorpusDownloadProcessor(BaseProcessor):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)

    def paginated_scan(self, table, scraper):
        last_evaluated_key = None
        while True:
            if last_evaluated_key:
                response = table.scan(
                    ExclusiveStartKey=last_evaluated_key,
                    FilterExpression=(
                        AttributeExists(Attr("text_storage_url"))
                        & Attr("scraper").eq(scraper)
                    ),
                )
            else:
                response = table.scan(
                    FilterExpression=(
                        AttributeExists(Attr("text_storage_url"))
                        & Attr("scraper").eq(scraper)
                    ),
                )
            last_evaluated_key = response.get("LastEvaluatedKey")

            for item in response["Items"]:
                yield item

            if not last_evaluated_key:
                break

    def run(self, documents: List[Any], **kwargs) -> List[Any]:
        output_dir: Path = kwargs.get("output_dir", Path(""))
        scrapers: List[str] = kwargs.get("scrapers", [])

        dynamodb = boto3.resource("dynamodb")
        s3 = boto3.resource("s3")
        table = dynamodb.Table("Documents")
        for scraper in scrapers:
            items = self.paginated_scan(table, scraper)
            output_path = output_dir / f"documents-{scraper}.jsonl"

            def get_text():
                for item in tqdm(items):
                    try:
                        obj = s3.Object(
                            "new-document-crawler", item["text_storage_url"]
                        )
                        item["text"] = obj.get()["Body"].read().decode("utf-8")
                        yield item
                    except Exception as e:
                        print(e)
                        continue

            srsly.write_jsonl(output_path, get_text())
        return self.component.run(documents, **kwargs)
