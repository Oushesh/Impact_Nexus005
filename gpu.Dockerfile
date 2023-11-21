FROM nvcr.io/nvidia/pytorch:21.10-py3

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y awscli

# set working directory
RUN mkdir /code
WORKDIR /code

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock /code/

# Allow installing dev dependencies to run tests
RUN bash -c "pip install --upgrade pip"
RUN pip install llvmlite --ignore-installed
RUN bash -c "poetry install --no-root --extras gpu"

COPY . /code/