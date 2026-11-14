# Yayın (deploy) için tek kutu: React derlenir, FastAPI hem oyunu hem /api'yi verir.
# Render bu dosyayı kendisi çalıştırır (render.yaml). Ayrıntı: README → "Yayınlama".

# 1) React arayüzünü derle (frontend/dist)
FROM node:22-slim AS web
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 2) Python sunucusu: oyunun beyni (data / calculations / artwork) + backend + derlenmiş arayüz
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY data.py calculations.py artwork.py ./
COPY backend/main.py backend/main.py
COPY --from=web /app/frontend/dist frontend/dist
# Render PORT değişkenini kendisi verir; yerelde 8000 kullanılır
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
