.PHONY: run-opensearch run install-dev install test lint

run-docker-dev:
	docker-compose up

run-docker-gpu:
	docker-compose -p entity-lookup-service_stack -f local_infra/docker-compose-local.yml up --build

run:
	cd Services && python3 manage.py runserver

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

local-infra:
	docker-compose -p entity-lookup-service_local_infra -f local_infra/docker-compose-local-infra.yml up --build

local-infra-gpu:


data:
	chmod 755 local_infra/put_data.sh && ./local_infra/put_data.sh

install-dev:
	python3 -m pip install -r requirements/dev.txt

install-common:
	python3 -m pip install -r requirements/prod.txt

install-prod:
	python3 -m pip install -r requirements/prod.txt

test:
	python3 -m pytest tests

lint:
	flake8

rest_api:
	python3 -m pip install -r requirements/rest_api.txt

postgres:

