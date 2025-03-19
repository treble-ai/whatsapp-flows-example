# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /app

# First copy only dependency files to leverage Docker caching
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies
RUN uv sync --frozen

# Then copy application code
COPY ./app ./app