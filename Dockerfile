FROM python:3.11-slim

WORKDIR /app

# Kopiujemy requirements z backend/
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy cały projekt
COPY . .

# Cloud Run używa portu 8080
ENV PORT=8080
EXPOSE 8080

# Uruchamiamy FastAPI przy użyciu uvicorn
# Zakładam, że main.py jest w folderze backend/
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
