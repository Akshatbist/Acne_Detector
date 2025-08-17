from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from io import BytesIO
from PIL import Image
import numpy as np
import os
import asyncio
from dotenv import load_dotenv

# --------------------
# Setup
# --------------------
load_dotenv()

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:5174",
    "http://localhost:5175",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.getenv("MODEL_PATH", r"C:\Users\aksha\ALL_PROJECTS\Acne_Detector\backend\app\AI_Model\runs\detect\train\weights\best.pt")
model = YOLO(MODEL_PATH)

# OPTIONAL: your custom label names (override model.names if desired)
ACNE_CLASSES = [
    "Whiteheads", "Blackheads", "Papules", "Pustules",
    "Nodules", "Cysts", "Post-Inflammatory Hyperpigmentation", "Scarring"
]

MAX_BYTES = 10 * 1024 * 1024        # 10 MB upload limit
MAX_DIM   = 4096                    # guard against image bombs

# --------------------
# Helpers
# --------------------
def _bytes_to_pil(img_bytes: bytes) -> Image.Image:
    try:
        img = Image.open(BytesIO(img_bytes))
        img = img.convert("RGB")
        if img.width > MAX_DIM or img.height > MAX_DIM:
            raise HTTPException(status_code=413, detail="Image dimensions too large")
        return img
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

def _format_detections(det) -> dict:
    """
    det: ultralytics.engine.results.Results
    """
    boxes = det.boxes
    if boxes is None or len(boxes) == 0:
        return {"num_detections": 0, "detections": []}

    data = boxes.data.cpu().numpy()  # Nx6: x1,y1,x2,y2,conf,cls
    names = ACNE_CLASSES if ACNE_CLASSES else det.names

    out = []
    for row in data:
        x1, y1, x2, y2, conf, cls_id = row
        cls_id = int(cls_id)
        out.append({
            "x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2),
            "confidence": float(conf),
            "class": cls_id,
            "class_name": names[cls_id] if 0 <= cls_id < len(names) else f"class_{cls_id}"
        })
    return {"num_detections": len(out), "detections": out}

async def _predict_in_thread(pil_img: Image.Image):
    # run the blocking model inference off the event loop
    return await asyncio.to_thread(model.predict, pil_img, verbose=False)

# --------------------
# Routes
# --------------------
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/detect")
async def detect(
    file: UploadFile = File(...),
    return_annotated: bool = Query(False, description="Return annotated JPEG instead of JSON"),
):
    # 1) read bytes into memory
    img_bytes = await file.read()
    if len(img_bytes) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image too large")

    # 2) decode safely
    pil_img = _bytes_to_pil(img_bytes)

    # 3) predict (no disk involved)
    results = await _predict_in_thread(pil_img)
    det = results[0]

    # 4) return JSON (default)
    payload = _format_detections(det)
    if not return_annotated:
        return JSONResponse(payload)

    # 5) or stream annotated image (still in-memory)
    annotated_bgr = det.plot()          # numpy array in BGR
    annotated_rgb = annotated_bgr[..., ::-1]
    buf = BytesIO()
    Image.fromarray(annotated_rgb).save(buf, format="JPEG", quality=90)
    buf.seek(0)

    # include a tiny JSON summary in a header if you want to read it client-side
    # (headers must be small; keep it minimal or omit if unnecessary)
    # after you format detections into `payload`
# e.g., payload = {"detections": [...]}  # trim to first N if many
    return StreamingResponse(buf, media_type="image/jpeg")


