from fastapi import APIRouter, File, UploadFile, HTTPException
from PIL import Image
from io import BytesIO
import tempfile
import uuid
import os
from ..services.cv import detect_objects

router = APIRouter()

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
ALLOWED_FILESIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/detect")
def detect(file: UploadFile = File(...)):
    filename = file.filename
    # print(f"Received file: {filename}")
    extension = filename[filename.rfind("."):].lower()

    # Validate file extension and size
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    contents = file.file.read()
    if len(contents) > ALLOWED_FILESIZE:
        raise HTTPException(status_code=400, detail="File size exceeds limit.")

    try:
        image = Image.open(BytesIO(contents))
        image.verify()  # Verify the image integrity
    except Exception as e:
        raise HTTPException(status_code=400, detail="Image is corrupted or invalid.")

    # Create a temporary directory for storing images
    temp_dir = tempfile.gettempdir()
    print(f"Temporary directory: {temp_dir}")

    
    # Generate unique identifiers for input and output images
    unique_id = str(uuid.uuid4())
    input_image_path = os.path.join(temp_dir, f"{unique_id}_input{extension}")
    output_image_path = os.path.join(temp_dir, f"{unique_id}_output{extension}")

    try:
        # Save the uploaded image to temporary storage
        with open(input_image_path, "wb") as temp_file:
            temp_file.write(contents)

        # Perform object detection
        detections = detect_objects(input_image_path, output_image_path)

        # Read the processed image
        with open(output_image_path, "rb") as processed_file:
            processed_image_data = processed_file.read()

        return {
            "filename": filename,
            "status": "File received and processed.",
            "detections": detections,
            "unique_id": unique_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

    finally:
        # Clean up temporary files
        for file_path in [input_image_path, output_image_path]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
    