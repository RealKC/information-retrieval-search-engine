FROM python:3.12-alpine3.21

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apk add clang

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

WORKDIR /app/Proiect/web-search
RUN CC=clang CXX=clang++ uv sync --frozen --no-cache

EXPOSE 5000

# Run the application.
CMD ["/app/.venv/bin/flask", "run", "--port", "5000" ]
