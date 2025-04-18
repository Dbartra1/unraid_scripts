FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt --progress-bar=on

# Copy the application folder and config folder
COPY /app /app
COPY /config /config

# Expose the required port
EXPOSE 8080

# Run the Python application
CMD ["python", "-u", "app.py"]