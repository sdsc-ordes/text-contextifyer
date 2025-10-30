# Use Python 3.11 as base image
FROM python:3.11-slim

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
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Run FastAPI server
CMD ["poetry", "run", "uvicorn", "text_contextifyer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
