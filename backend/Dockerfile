FROM python:3.12-slim

# System libs for OpenCV/Torch/YOLO; libgl1 fixes libGL.so.1
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libjpeg62-turbo libpng16-16 libtiff6 libopenblas0 libgomp1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel --no-cache-dir \
    && pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app

# Runtime config
ENV PORT=8000
# Change if your FastAPI instance is elsewhere
ENV APP_MODULE="app.main:app"

EXPOSE 8000

# Run via python -m so we don’t rely on a uvicorn binary on PATH
CMD sh -c 'python -m uvicorn ${APP_MODULE:-app.main:app} --host 0.0.0.0 --port ${PORT:-8000}'
