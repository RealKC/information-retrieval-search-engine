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

WORKDIR /app/Proiect/url_frontier
RUN uv sync --frozen --no-cache

# Run the application.
EXPOSE 8080
CMD ["/app/.venv/bin/fastapi", "run", "/app/Proiect/url_frontier/main.py", "--port", "8080", "--host", "0.0.0.0"]
