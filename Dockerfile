# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container at /app
COPY . .

# Expose any ports your app needs (adjust as necessary)
EXPOSE 8080

# Run the Python script (adjust this if you have an entry point script)
CMD ["python", "your_script.py"]
