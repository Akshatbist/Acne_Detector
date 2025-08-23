FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libjpeg62-turbo libpng16-16 libtiff6 libopenblas0 libgomp1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel --no-cache-dir \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app

# If main.py is at repo root
ENV APP_MODULE="main:app"

# Default, but Railway will override with its own $PORT
ENV PORT=8000

# ...
EXPOSE 8000

# Expand env at runtime (Railway sets PORT)
CMD ["sh","-c","python -m uvicorn ${APP_MODULE:-main:app} --host 0.0.0.0 --port ${PORT:-8000}"]


