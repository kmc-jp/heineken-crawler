FROM python:slim

WORKDIR /app

RUN pip install poetry

COPY ./poetry.lock ./pyproject.toml /app/
RUN poetry install --no-dev

COPY . /app/

ENTRYPOINT ["poetry", "run", "python3"]
