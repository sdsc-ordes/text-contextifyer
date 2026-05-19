# Use Python 3.11 as base image
FROM python:3.11-slim

LABEL org.opencontainers.image.source=https://github.com/sdsc-ordes/text-contextifyer

# Set working directory
WORKDIR /app

# Install poetry with latest stable version
RUN pip install poetry==2.2.1

# Copy dependency files for better layer caching
COPY pyproject.toml poetry.lock* ./

# Configure poetry
RUN poetry config virtualenvs.create false && \
    poetry config installer.max-workers 4

# Install production dependencies only
RUN poetry install --without dev --no-interaction --no-ansi --no-root

# Copy source code and install the project
COPY src/ src/
RUN poetry install --only-root --no-interaction --no-ansi

# Expose port for FastAPI

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PORT=8001
EXPOSE ${PORT}
# Run FastAPI server
CMD ["sh", "-c", "poetry run uvicorn text_contextifyer.api.main:app --host 0.0.0.0 --port ${PORT}"]
