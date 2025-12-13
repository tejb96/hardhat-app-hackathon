from ultralytics import YOLO


MODEL_NAME = "models/best.pt"

# Load a model
try:
    model = YOLO(MODEL_NAME)
    print(f"Classes: {model.names}")
except Exception as e:
    raise RuntimeError(f"Failed to load model '{MODEL_NAME}': {e}")


def detect_objects(image_path: str, output_path: str):
    """
    Detect objects in an image and save the annotated image.
    
    Args:
        image_path: Path to the input image
        output_path: Path where the processed image will be saved
    
    Returns:
        List of detections with confidence scores and bounding boxes
    """
    try:
        results = model(
            image_path,
            conf=0.25,   # confidence threshold
            iou=0.45,    # IoU threshold for NMS
            agnostic_nms=False,
            max_det=1000
        )

        print(results)
        # for r in results:
        #     print(r.boxes)
        detections = results[0].boxes.data.tolist()  # Get detection results


        
        # Save the annotated image
        annotated_image = results[0].plot(save=True,filename=output_path)  # Get annotated image array
        
        return detections
    except Exception as e:
        raise RuntimeError(f"Detection failed: {e}")
