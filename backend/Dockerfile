FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (build tools and tesseract OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create the data folder for SQLite persistent storage
RUN mkdir -p /app/data

EXPOSE 8000

# Set default database path env to point to the persistent data volume
ENV DATABASE_PATH=/app/data/statements.db

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
