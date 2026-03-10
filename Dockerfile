FROM python:3.11-slim

WORKDIR /app

# Kopiujemy plik z wymaganiami z podfolderu backend
COPY backend/requirements.txt .

# Instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę kodu (zakładając, że chcesz skopiować wszystko)
COPY . .

# Jeśli Twoja aplikacja startuje z pliku w folderze backend, to wskazujemy ścieżkę
ENV PORT=8080
EXPOSE 8080

# Podstawiamy tutaj komendę, którą uruchamiasz backend
CMD ["python", "backend/main.py"]
