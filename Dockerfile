FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ bot/
COPY main.py .
COPY assets/ assets/

RUN mkdir -p /app/data

ENV DATA_DIR=/app/data
ENV ASSETS_DIR=/app/assets

CMD ["python", "-u", "main.py"]
