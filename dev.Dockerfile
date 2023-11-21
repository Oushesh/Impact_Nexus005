# syntax=docker/dockerfile:1
FROM python:3.10.0

ARG PORT=8000
LABEL maintainer="oushesh"
ENV PYTHONUNBUFFERED 1

WORKDIR /Services/services_project
COPY requirements/dev.txt /Services/services_project/

RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements/dev.txt

COPY . /Services/services_project/

RUN chmod a+x /Services/services_project/dev-docker-entrypoint.sh
ENTRYPOINT ["/Services/services_project/dev-docker-entrypoint.sh"]
