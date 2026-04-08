FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy uv dependency files
COPY pyproject.toml ./
# Copy uv.lock if it exists, otherwise just pyproject.toml
COPY uv.lock* ./

# Install dependencies without installing the project itself
RUN uv sync --frozen --no-install-project || uv sync --no-install-project

# Copy the rest of the application
COPY . .

# Ensure data directory exists
RUN mkdir -p data

# Run Alembic upgrade before starting the server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn main:app --host 0.0.0.0 --port 8000"]