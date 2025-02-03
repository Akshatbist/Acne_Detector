from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
import os
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

#Initialize
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

#Upload directory for users to upload images
UPLOAD_DIR = os.getenv("UPLOAD_DIR")
os.makedirs(UPLOAD_DIR, exist_ok=True)

PREDICT_DIR = os.getenv("PREDICT_DIR")
os.makedirs(PREDICT_DIR, exist_ok=True)
# Adds static path to the server
app.mount("/predict", StaticFiles(directory=PREDICT_DIR), name="predict")

model = YOLO(os.getenv("MODEL_PATH"))

executor = ThreadPoolExecutor(max_workers=4)

# Define a function to run YOLO inference in a separate thread
def run_yolo_inference(file_path: str):
    results = model.predict(source=file_path, save = True, project="runs/detect", name="predict", exist_ok=True)  # Run YOLO inference
    print(f"Results for {file_path}: {results}")

    detect_folder = os.path.join("runs", "detect", "predict")

    if not os.path.exists(detect_folder):  # Check if folder exists
        return None
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]  # Get the base name of the file
    image_files = os.path.join(detect_folder, f"{base_name}.jpg") # Get the path to the processed image

    if not image_files:  # No images found
        return None

    processed_image = image_files  

    return results, processed_image

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # Save the uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Run YOLO inference asynchronously
    loop = asyncio.get_event_loop()
    results, processed_image = await loop.run_in_executor(executor, run_yolo_inference, file_path)

    # Extract and format YOLO results
    detections = results[0].boxes.data.tolist()
    print(detections)
    ACNE_CLASSES = ["Whiteheads", "Blackheads", "Papules", "Pustules", "Nodules", "Cysts", "Post-Inflammatory Hyperpigmentation", "Scarring"]
    formatted_results = [
        {
            "x1": int(box[0]),
            "y1": int(box[1]),
            "x2": int(box[2]),
            "y2": int(box[3]),
            "confidence": float(box[4]),
            "class": int(box[5]),
            "class_name": ACNE_CLASSES[int(box[5])] if int(box[5]) < len(ACNE_CLASSES) else "Unknown"
        }
        for box in detections
    ]

    print(f"Raw results: {results}")  # Logs entire YOLO results
    print(f"Detections: {results[0].boxes.data.tolist() if results[0].boxes else 'No detections'}")


    return JSONResponse(content={
            "detections": formatted_results,
            "image_url": f"/predict/{os.path.basename(processed_image)}" if processed_image else None
        })

