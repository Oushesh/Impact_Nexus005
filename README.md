# smart-evidence

```bash
# setup dev environment
$ poetry install --with dev

# create .env file and fill in the secret credentials from the nextcloud password file
cp .env.template .env
```

* This project is using spaCy projects, read [here](https://spacy.io/usage/projects) for details. Don't forget to update this document after updating `project.yml` with the command `python -m spacy project document --output README.md`

## Running the pipeline for local development

* Prepare data for the pipeline:

  ```bash
  python -m spacy project run download-test-corpus
  ```

* Always check the `project.yml` file for setting the variables before running the pipeline. Set gpu_id to -1 for cpu setup.
* Clean up indices on ElasticSearch by running following command on dev console: `DELETE \documents_dev` and `DELETE \insights_dev`

* Build and execute docker container with compose `docker-compose up --build`
* Attach a shell inside using VSCode docker extension or `docker container ls`, copy container id for smart-evidence and execute `docker exec -it [container_id] bash`
* Prepare spacy pipeline

  ```bash
  python -m spacy project run package-and-install-entity-pipeline-cpu
  ```

* Index documents and insights into elastic search

  ```bash
  python -m spacy project run index
  ```

* Annotate insights in elastic search
  ```python -m spacy project run annotate```

Now, documents and insights should be available in the indices set in `project.yml` vars section.

<!-- SPACY PROJECT: AUTO-GENERATED DOCS START (do not remove) -->

# 🪐 spaCy Project: Nexus

NLP pipeline of ImpactNexus

## 📋 project.yml

The [`project.yml`](project.yml) defines the data assets required by the
project, as well as the available commands and workflows. For details, see the
[spaCy projects documentation](https://spacy.io/usage/projects).

### ⏯ Commands

The following commands are defined by the project. They
can be executed using [`spacy project run [name]`](https://spacy.io/api/cli#project-run).
Commands are only re-run if their inputs have changed.

| Command | Description |
| --- | --- |
| `download-pipeline` | Download the pretrained pipeline |
| `download-insight-classifier` | Download the pretrained insight classifier |
| `download-boolqa-concept-relation-classifier` | Download the pretrained boolqa style company impact classifier |
| `create-documents` | Create documents jsonl from scraping index in dynamoDB |
| `upload-corpus` | Upload all corpus |
| `download-corpus` | Download all corpus |
| `download-test-corpus` | Download test corpus |
| `package-and-install-entity-pipeline-cpu` | Create spacy package for en_ix_entity_ruler pipeline |
| `package-and-install-entity-pipeline` | Create spacy package for en_ix_entity_ruler pipeline |
| `upload-package-entity-pipeline` |  |
| `extract-documents` | Extract document from scrape index. |
| `extract-insights` | Extract document elements, e.g. paragraphs, abstract from documents. |
| `annotate-insights` | Annotate insights |
| `generate-annotation-tasks` | Annotate insights |
| `serve-dev` |  |

### ⏭ Workflows

The following workflows are defined by the project. They
can be executed using [`spacy project run [name]`](https://spacy.io/api/cli#project-run)
and will run the specified commands in order. Commands are only re-run if their
inputs have changed.

| Workflow | Steps |
| --- | --- |
| `create-corpus` | `create-documents` &rarr; `upload-corpus` |
| `prepare` | `package-and-install-entity-pipeline` &rarr; `download-corpus` |
| `index` | `extract-documents` &rarr; `extract-insights` |

<!-- SPACY PROJECT: AUTO-GENERATED DOCS END (do not remove) -->


