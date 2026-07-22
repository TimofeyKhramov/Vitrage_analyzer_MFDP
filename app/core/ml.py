from app.core.config import settings
from ultralytics import YOLO


model_drawings = YOLO(settings.drawings_model_path)

model_doors = YOLO(settings.doors_model_path)