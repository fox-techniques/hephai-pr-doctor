FROM python:3.10-slim

# Set up the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy necessary files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --only main

# Copy the application files
COPY action/ ./action/

# Set entrypoint
ENTRYPOINT ["poetry", "run", "python", "action/main.py"]
