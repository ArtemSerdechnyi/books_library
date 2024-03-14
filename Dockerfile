FROM python:3.12.2-alpine3.19
LABEL authors="artem"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build tools
RUN apk add --no-cache make

# Install poetry
RUN pip install --no-cache-dir poetry

# Set working directory
WORKDIR /code

# Copy poetry files
COPY pyproject.toml poetry.lock /code/

# Install project dependencies using poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Copy makefile
COPY Makefile /code/

# Copy project files
COPY src/ /code/

# Expose port
EXPOSE 8000