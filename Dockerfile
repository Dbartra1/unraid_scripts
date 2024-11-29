# Build stage
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
EXPOSE 8080
EXPOSE 5000
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /app .
COPY . .
EXPOSE 8080
EXPOSE 5000
CMD ["python", "app.py"]