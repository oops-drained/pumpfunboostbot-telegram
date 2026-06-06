FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ bot/
COPY admin/ admin/
COPY main.py .
COPY admin_main.py .
COPY start.py .
COPY assets/ assets/

# Dokploy writes .env from the Environment tab before docker build (createEnvFile).
COPY .env /app/.env

RUN mkdir -p /app/data

ENV DATA_DIR=/app/data
ENV ASSETS_DIR=/app/assets
ENV APP_MODE=bot

CMD ["python", "-u", "start.py"]
