<<<<<<< HEAD
FROM node:20-alpine

WORKDIR /app

# Jeśli Wika wygeneruje projekt, skopiujemy paczki. Jeśli nie, kontener i tak wystartuje.
COPY package.json package-lock.json* ./
RUN npm install || echo "Brak package.json, pomijam instalację."

COPY . .

EXPOSE 5173

# Odpalenie Vite w trybie nasłuchiwania na wszystkie interfejsy
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
=======
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
>>>>>>> 554b72cd3f54642d553af0af465697b466903de1
