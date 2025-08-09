FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ ./app/
COPY config/ ./config/

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose the Flask port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.app
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "-m", "app.app"]