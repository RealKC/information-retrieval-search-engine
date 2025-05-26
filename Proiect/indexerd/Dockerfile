FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates clang

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN ls
RUN uv sync --frozen --no-cache

WORKDIR /app/Proiect/indexerd
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["uv", "run", "/app/Proiect/indexerd/main.py"]
