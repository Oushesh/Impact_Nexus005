FROM python:3.10.10

# Install system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y awscli

# Set the working directory
WORKDIR /code

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    mv /root/.local/bin/poetry /usr/local/bin/poetry

# Copy only the dependencies files to take advantage of caching
COPY pyproject.toml poetry.lock* /code/

# Install Poetry dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# Copy the rest of the application code
COPY . /code/

# Allow installing dev dependencies to run tests (if needed)
RUN poetry install --no-root --extras dev

CMD ["poetry", "run", "your_command_here"]


# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /code/

# Allow installing dev dependencies to run tests
RUN bash -c "pip install --upgrade pip"
RUN bash -c "poetry install --no-root"

COPY . /code/

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /code/

# Allow installing dev dependencies to run tests
RUN bash -c "pip install --upgrade pip"
RUN bash -c "poetry install --no-root"

COPY . /code/
