# train using yolo segment
import os
import sys
import ultralytics
from ultralytics import YOLO

from ultralytics import YOLO

def train_coin_model():
    model = YOLO("yolo11m-seg.pt")  # or yolov8s-seg.pt
    model.train(
        data="coins_train/data.yaml",
        epochs=20,
        imgsz=640,
        batch=16,
        task="segment",
        name="coin_model"
    )
    model.save("coin_model.pt")

if __name__ == "__main__":
    train_coin_model()
