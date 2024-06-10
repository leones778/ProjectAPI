FROM python:3.12.3-alpine3.18

WORKDIR /code

RUN pip install poetry

COPY pyproject.toml poetry.lock /code/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev

COPY /app /code/app
COPY alembic.ini /code/
ENV PYTHONPATH=/code