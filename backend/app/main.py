from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from io import BytesIO
from PIL import Image
from pathlib import Path
import numpy as np
import os, json, asyncio
from dotenv import load_dotenv

# --------------------
# Setup
# --------------------
load_dotenv()

app = FastAPI()

# Allow localhost + 127.0.0.1 (Vite usually 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Detections"],  # so browser can read this header
)

# Resolve model path: env override; else relative to this file
BASE_DIR = Path(__file__).resolve().parent
default_model = BASE_DIR / "AI_Model" / "runs" / "detect" / "train" / "weights" / "best.pt"
env_model = os.getenv("MODEL_PATH")
MODEL_PATH = Path(env_model).expanduser().resolve() if env_model else default_model

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"MODEL_PATH does not exist: {MODEL_PATH}")

model = YOLO(str(MODEL_PATH))

# OPTIONAL: your custom label names (override model.names if desired)
ACNE_CLASSES = [
    "Whiteheads", "Blackheads", "Papules", "Pustules",
    "Nodules", "Cysts", "Post-Inflammatory Hyperpigmentation", "Scarring"
]

MAX_BYTES = 10 * 1024 * 1024        # 10 MB upload limit
MAX_DIM   = 4096                    # guard against image bombs

# --------------------
# Startup warmup (prevents first-run stall)
# --------------------
@app.on_event("startup")
async def warmup():
    try:
        dummy = Image.fromarray(np.zeros((640, 640, 3), dtype=np.uint8))
        print(">> warmup start")
        _ = await asyncio.to_thread(
            model.predict, dummy, verbose=False, imgsz=640, device="cpu"
        )
        print(">> warmup done")
    except Exception as e:
        print(">> warmup failed:", e)

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
    return await asyncio.to_thread(
        model.predict,
        pil_img,
        verbose=False,
        imgsz=640,     # speed/quality knob; try 512/416 if slow
        device="cpu",
        conf=0.25
    )

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
    print(">> /detect called")
    # 1) read bytes into memory
    img_bytes = await file.read()
    if len(img_bytes) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image too large")

    # 2) decode safely
    pil_img = _bytes_to_pil(img_bytes)
    print(">> decoded")

    # 3) predict (no disk involved)
    results = await _predict_in_thread(pil_img)
    det = results[0]
    print(">> predicted")

    # 4) JSON by default
    payload = _format_detections(det)
    if not return_annotated:
        print(">> returning JSON")
        return JSONResponse(payload)

    # 5) or stream annotated image (still in-memory)
    annotated_bgr = det.plot()          # numpy array in BGR
    annotated_rgb = annotated_bgr[..., ::-1]
    buf = BytesIO()
    Image.fromarray(annotated_rgb).save(buf, format="JPEG", quality=90)
    buf.seek(0)
    print(">> returning JPEG stream")

    # Optional: tiny header with a few detections
    header_payload = {"detections": payload["detections"][:8]}  # keep small!
    headers = {"X-Detections": json.dumps(header_payload)}

    return StreamingResponse(buf, media_type="image/jpeg", headers=headers)
