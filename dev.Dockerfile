# syntax=docker/dockerfile:1
FROM python:3.10.0
ARG PORT=8000
LABEL maintainer="oushesh"
ENV PYTHONUNBUFFERED 1

WORKDIR /services_project
COPY requirements/dev.txt Services/services_project/

RUN apt update && \
	apt install build-essential && \
	rm -rf /var/cache/apk/* && \
	pip install --upgrade pip && \
	pip install --no-cache-dir -r dev.txt

COPY . /services_project/

RUN chmod a+x /services_project/dev-docker-entrypoint.sh
ENTRYPOINT ["/services_project/dev-docker-entrypoint.sh"]
