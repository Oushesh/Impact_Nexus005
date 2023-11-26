"""
https://fasttext.cc/docs/en/unsupervised-tutorial.html
"""

import fasttext
import typer
from pathlib import Path


def build_word_vectors(
    input_folder: Path = Path("fastText/data/knowledge_base_paragraphs"),
    output_folder: Path = Path("fastText/results/knowledge_base_paragraphs-d300"),
    model_name: str = "skipgram",
    minn: int = 2,
    maxn: int = 6,
    dim: int = 300,
    ws: int = 5,
):
    model = fasttext.train_unsupervised(
        str(input_folder), model_name, minn=minn, maxn=maxn, dim=dim, ws=ws
    )

    model.save_model(str(output_folder))


if __name__ == "__main__":
    typer.run(build_word_vectors)
