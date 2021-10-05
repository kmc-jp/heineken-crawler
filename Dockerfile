FROM python:slim

WORKDIR /app

ENV PYTHONBUFFERED=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install poetry

COPY ./poetry.lock ./pyproject.toml /app/
RUN poetry install --no-dev

COPY . /app/

ENTRYPOINT ["poetry", "run", "python3"]
