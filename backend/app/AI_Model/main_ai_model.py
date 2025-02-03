from ultralytics import YOLO

model = YOLO("yolov8s.pt")

results = model.train(data=r"C:\Users\aksha\ALL_PROJECTS\Acne_Detector\backend\app\AI_Model\config.yaml", epochs = 100)