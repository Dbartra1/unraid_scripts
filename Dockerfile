FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
COPY .env /app/.env
COPY . .
EXPOSE 8080
EXPOSE 5000
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]