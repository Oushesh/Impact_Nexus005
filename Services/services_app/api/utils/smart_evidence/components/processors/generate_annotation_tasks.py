from app.models.impact_screening import Insight
from .base_processor import BaseProcessor


class GenerateAnnotationTasks(BaseProcessor):
    def process(self, sample):
        insight = Insight(**sample.dict(exclude_none=True))
        tasks = sample.get_annotation_by(self.config.get("experiment_name")).tasks
        return {
            **insight.dict(),
            "annotation": tasks.dict(),
        }

    def run(self, batch):
        return self.component.run([self.process(sample) for sample in batch])
