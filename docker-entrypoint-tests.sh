#! /usr/bin/env sh

python -m spacy project run package-and-install-entity-pipeline-cpu

cd tests

pytest

# python -m spacy project run download-corpus-test

# python -m spacy project run index
