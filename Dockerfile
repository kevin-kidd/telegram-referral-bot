FROM python:3.9.18-slim

# Install dependencies and clean up in one layer
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .


CMD ["python", "main.py"]