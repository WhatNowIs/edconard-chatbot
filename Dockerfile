# ======= BASE IMAGE ==========
FROM python:3.11

WORKDIR /app

# Add the necessary paths to PYTHONPATH
ENV PYTHONPATH=/app:/app/create_llama/backend
# Add Poetry's binary path to the PATH environment variable
ENV PATH="/root/.local/bin:$PATH"

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python && \
    poetry config virtualenvs.create false

# Copy Poetry configuration and install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Copy the rest of the application code
COPY . .

# Ensure the required directories exist
RUN mkdir -p data storage images

# Expose the application port
EXPOSE 8080

# Command to run the application
CMD ["python", "main.py"]
