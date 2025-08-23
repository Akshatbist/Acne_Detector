FROM python:3.12-slim

# System libs for OpenCV/Torch/YOLO
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libjpeg62-turbo libpng16-16 libtiff6 libopenblas0 libgomp1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- adjust these two lines if your requirements are elsewhere ---
# If your requirements.txt is at repo root:
COPY requirements.txt /tmp/requirements.txt
# If it’s at backend/requirements.txt, use:
# COPY backend/requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel --no-cache-dir \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# Set the workdir to the folder that contains main.py
WORKDIR /backend/app
# Copy ONLY the backend/app code into the image (faster builds)
COPY backend/app /backend/app

# Uvicorn target -> backend/app/main.py contains `app = FastAPI(...)`
ENV APP_MODULE="main:app"

# Expose is optional for Railway, but harmless
EXPOSE 8000

# IMPORTANT: no ${PORT:-8000}. Railway sets $PORT.
# Use shell-form CMD so $PORT expands.
CMD python -m uvicorn ${APP_MODULE} --host 0.0.0.0 --port $PORT
