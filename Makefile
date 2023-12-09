.PHONY: run-opensearch run install-dev install test lint

run-docker-dev:
	docker-compose up

run-docker-gpu:
	docker-compose-gpu
run-docker-rest-api:
	docker-compose-rest-api

run-smart-evidence:
	docker-compose-smart-evidence

run:
	export PYTORCH_ENABLE_MPS_FALLBACK=1 && cd Services && python3 manage.py runserver

run-server:
	/bin/sh run_server.sh

dynamodb:
	docker run -p 8000:8000 amazon/dynamodb-local

redis:
	docker run -d --name redis-stack-server -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

opensearch:
	docker run -d --name opensearch -p 9200:9200 -p 9600:9600 \
	-e "cluster.name=telescope-opensearch-cluster" \
    -e "bootstrap.memory_lock=true" \
    -e "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m" \
    -e "DISABLE_INSTALL_DEMO_CONFIG=true" \
    -e "plugins.security.disabled=true" \
    -e "discovery.type=single-node" \
    opensearchproject/opensearch:1.2.0

download-data:
	bash bash-scripts/download_blink_models.sh

models:
	aws sync models

install-dev:
	python3 -m venv dev_venv && \
    	. dev_venv/bin/activate && \
    	python3 -m pip install -r requirements/dev.txt

install-common:
	python3 -m venv common_venv && \
      . common_venv/bin/activate && \
      python3 -m pip install -r requirements/common.txt

install-prod:
	python3 -m venv prod_venv && \
        . prod_venv/bin/activate && \
        python3 -m pip install -r requirements/prod.txt

test:
	python3 -m pytest tests

lint:
	flake8

rest_api-local:
	python3 -m venv rest_api_venv && \
        . rest_api_venv/bin/activate && \
        python3 -m pip install -r requirements/rest_api.txt

aws-ecr:
	echo Logging in to Amazon ECR...
	aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
	echo Build started on `date`
	echo Building the Docker image...
	docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG .
	docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
	echo Build completed on `date`
	echo Pushing the Docker image...
	docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG

sync-models-local:
	gsutil -m rsync -r gs://dvc_models_bucket models

sync-models-gcp:
	gsutil -m rsync -r models gs://dvc_models_bucket


install-precommit:
	pre-commit install

run-precommit:
	pre-commit run

install-elasticseach:
	docker pull docker.elastic.co/elasticsearch/elasticsearch:7.9.2
	docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.9.2

install-milvus:
	pip install -e "git+https://github.com/deepset-ai/haystack-extras.git#egg=milvus_documentstore&subdirectory=stores/milvus-documentstore"

install-opensearch:
	docker pull opensearchproject/opensearch:1.0.1
	docker run -p 9200:9200 -p 9600:9600 -e "discovery.type=single-node" opensearchproject/opensearch:1.0.1

install-qdrant:
	pip install qdrant-haystack


install-weaviate:
	docker run -d -p 8080:8080 --env AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED='true' --env PERSISTENCE_DATA_PATH='/var/lib/weaviate' semitechnologies/weaviate:1.17.2

