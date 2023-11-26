from pathlib import Path
from typing import Any

import srsly
import glob

from smart_evidence.components.base_component import BaseComponent
from smart_evidence.components.data_stores.base_store import BaseStore


class JSONLStore(BaseStore):
    def __init__(self, component: BaseComponent, **data):
        super().__init__(component=component, **data)
        if self.mode == "write":
            self.outfile = Path(self.component_config["outfile"])
            assert not self.outfile.exists(), "Outfile exists"
            self.outfile.parent.mkdir(exist_ok=True, parents=True)
        elif self.mode == "read":
            self.infile = Path(self.component_config["infile"])

    def write_batch(self, batch: Any, **kwds):  # pylint: disable=W0613
        srsly.write_jsonl(
            self.outfile,
            [
                i.dict(
                    exclude_none=True,
                    exclude=set(self.exclude_fields),
                )
                for i in batch
            ],
            append=True,
            append_new_line=False,
        )

    def item_generator(self, **kwds):  # pylint: disable=W0613
        filepaths = glob.glob(str(self.infile))
        assert filepaths, "There are no files in infile pattern for the JSONL Store"
        for filepath in filepaths:
            return srsly.read_jsonl(filepath)
