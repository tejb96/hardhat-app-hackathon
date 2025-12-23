from ultralytics import YOLO
from typing import List, Dict, Any
import os

MODEL_NAME = "models/best.pt"

# Load model once
try:
    model = YOLO(MODEL_NAME)
    print(f"Model loaded successfully.")
    print(f"Classes: {model.names}")
except Exception as e:
    raise RuntimeError(f"Failed to load model '{MODEL_NAME}': {e}")


def detect_objects(
    image_path: str,
    output_image_path: str | None = None
) -> Dict[str, Any]:
    """
    Run YOLO inference and return structured results.
    
    If output_image_path is provided, saves the annotated image there.
    """
    try:
        # Run inference with save=False (we'll handle saving manually if requested)
        results = model(
            image_path,
            conf=0.25,
            iou=0.45,
            agnostic_nms=False,
            max_det=1000,
            save=False,           # We don't want auto-save to runs/detect
            imgsz=640,            # Optional: explicit size
            verbose=False
        )[0]

        boxes = results.boxes
        detections: List[Dict] = []
        average_confidence = 0.0

        if boxes is not None and len(boxes) > 0:
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i].item())
                class_name = model.names[cls_id]
                confidence = round(boxes.conf[i].item(), 3)
                x1, y1, x2, y2 = map(round, boxes.xyxy[i].tolist())

                average_confidence += confidence

                detections.append({
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2]
                })

            average_confidence = round(average_confidence / len(boxes), 3)
        else:
            average_confidence = 0.0

        # Summary logic
        hardhat_count = sum(1 for d in detections if d["class_name"] == "Hardhat")
        no_hardhat_count = sum(1 for d in detections if d["class_name"] == "NO-Hardhat")
        total_persons = hardhat_count + no_hardhat_count
        total_infractions = no_hardhat_count

        summary = {
            "total_persons": total_persons,
            "wearing_hardhat": hardhat_count,
            "missing_hardhat": no_hardhat_count,
            "total_infractions": total_infractions,
            "average_confidence": round(average_confidence * 100, 1)
        }

        # Save annotated image if path is provided
        if output_image_path is not None:
            # Use Ultralytics' built-in plot method to get annotated image
            annotated_img = results.plot()  # Returns numpy array with boxes/labels drawn
            results.save(filename=output_image_path)  # Best method: uses same logic as save=True
            # Alternatively: cv2.imwrite(output_image_path, annotated_img[:, :, ::-1]) if you prefer

        return {
            "summary": summary,
            "detections": detections
        }

    except Exception as e:
        raise RuntimeError(f"Detection failed: {e}")
    finally:
        # Only clean up input image if we're responsible for it (i.e., in router temp flow)
        # We'll keep this for backward compatibility, but in new flow we'll manage cleanup outside
        if os.path.exists(image_path) and output_image_path is None:  # Only clean if no session
            try:
                os.remove(image_path)
            except OSError:
                pass