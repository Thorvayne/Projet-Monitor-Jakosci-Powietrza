FROM python:3.11-slim

WORKDIR /app

# Copy requirements from the correct relative path
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# IMPORTANT: Remove EXPOSE 8000. Cloud Run ignores it anyway.
# Use the $PORT environment variable and remove --reload (not for production)
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
