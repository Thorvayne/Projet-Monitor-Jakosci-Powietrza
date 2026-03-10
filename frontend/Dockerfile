FROM node:20-alpine

WORKDIR /app

# Jeśli Wika wygeneruje projekt, skopiujemy paczki. Jeśli nie, kontener i tak wystartuje.
COPY package.json package-lock.json* ./
RUN npm install || echo "Brak package.json, pomijam instalację."

COPY . .

EXPOSE 5173

# Odpalenie Vite w trybie nasłuchiwania na wszystkie interfejsy
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
