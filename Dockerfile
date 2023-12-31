FROM python:slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN apt update && apt install -y libxml2-dev libxslt1-dev

RUN pip install poetry

COPY ./poetry.lock ./pyproject.toml /app/
RUN poetry install --no-dev

COPY . /app/

ENTRYPOINT ["poetry", "run", "python3"]
