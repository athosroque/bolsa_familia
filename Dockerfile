FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2 if needed (slim often needs libpq-dev)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command (can be overridden)
CMD ["python", "src/etl/extract_bolsa_familia.py"]
