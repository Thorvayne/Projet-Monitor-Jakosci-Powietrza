FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run używa portu 8080 jako domyślnego
ENV PORT=8080
EXPOSE 8080

# Używamy gunicorn (zalecane dla środowisk produkcyjnych jak Cloud Run)
# Jeśli nie masz gunicorna, zainstaluj go w requirements.txt
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 backend.main:app
