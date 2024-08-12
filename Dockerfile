FROM python:3.9.18-slim

# Create a non-root user and group
RUN groupadd -r kevin && useradd -r -g kevin kevin

# Set the working directory and change its ownership
WORKDIR /app
RUN chown -R kevin:kevin /app && chmod -R 755 /app

# Install dependencies and clean up in one layer
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY --chown=kevin:kevin . .

# Switch to the non-root user
USER kevin

CMD ["python", "main.py"]