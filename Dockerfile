FROM python:3.9.18-slim

# Create a non-root user
RUN useradd -m -s /bin/bash appuser

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc \
    && rm -rf /var/lib/apt/lists/*

# Create coverage directory and set permissions
RUN mkdir /coverage_data && chown appuser:appuser /coverage_data && chmod 755 /coverage_data

COPY . .

# Change ownership of the /app directory to appuser
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

CMD ["python", "main.py"]