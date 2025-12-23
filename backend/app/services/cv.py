from ultralytics import YOLO
from typing import List, Dict, Any
import os

MODEL_NAME = "models/best.pt"

# Load model once
try:
    model = YOLO(MODEL_NAME)
    print(f"Model loaded successfully.")
    print(f"Classes: {model.names}")  # {0: 'Hardhat', 1: 'NO-Hardhat'}
except Exception as e:
    raise RuntimeError(f"Failed to load model '{MODEL_NAME}': {e}")


def detect_objects(image_path: str) -> Dict[str, Any]:
    """
    Run YOLO inference and return structured results for Hardhat / NO-Hardhat classes.
    No annotated image is saved.
    """
    try:
        results = model(
            image_path,
            conf=0.25,
            iou=0.45,
            agnostic_nms=False,
            max_det=1000
        )[0]

        boxes = results.boxes
        detections: List[Dict] = []
        averageConfidence = 0.0

        for i in range(len(boxes)):
            cls_id = int(boxes.cls[i].item())
            class_name = model.names[cls_id]
            confidence = round(boxes.conf[i].item(), 3)
            x1, y1, x2, y2 = map(round, boxes.xyxy[i].tolist())

            averageConfidence += confidence

            detections.append({
                "class_name": class_name,
                "confidence": confidence,
                "bbox": [x1, y1, x2, y2]
            })
        
        averageConfidence = round(averageConfidence / len(boxes), 3) if len(boxes) > 0 else 0.0

        # Compute summary based on your actual classes
        hardhat_count = sum(1 for d in detections if d["class_name"] == "Hardhat")
        no_hardhat_count = sum(1 for d in detections if d["class_name"] == "NO-Hardhat")
        total_persons = hardhat_count + no_hardhat_count
        total_infractions = no_hardhat_count  

        summary = {
            "total_persons": total_persons,
            "wearing_hardhat": hardhat_count,
            "missing_hardhat": no_hardhat_count,
            "total_infractions": total_infractions,
            # "compliance_rate": (
            #     round((hardhat_count / total_persons) * 100, 1) if total_persons > 0 else 0
            # ),
            "average_confidence": averageConfidence*100
        }

        return {
            "summary": summary,
            "detections": detections
        }

    except Exception as e:
        raise RuntimeError(f"Detection failed: {e}")
    finally:
        # Clean up temp image immediately
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except OSError:
                pass