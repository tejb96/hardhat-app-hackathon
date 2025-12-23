from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
import tempfile
import uuid
import os
from ..services.cv import detect_objects  # Now returns dict with summary + detections

router = APIRouter()

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_FILESIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/detect")
async def detect(file: UploadFile = File(...)):
    filename = file.filename or "uploaded_image"
    extension = os.path.splitext(filename)[1].lower()

    # Validate extension
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: PNG, JPG, JPEG, WEBP.")

    # Read and validate size
    contents = await file.read()
    if len(contents) > ALLOWED_FILESIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

    # Validate it's a real image
    try:
        Image.open(BytesIO(contents)).verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file.")

    # Create unique temp path for inference
    unique_id = str(uuid.uuid4())
    temp_input_path = os.path.join(tempfile.gettempdir(), f"{unique_id}_input{extension}")

    try:
        # Save uploaded image temporarily
        with open(temp_input_path, "wb") as f:
            f.write(contents)

        # Run detection → get structured results (no output image saved)
        result_data = detect_objects(temp_input_path)

        # Return clean JSON response
        return JSONResponse(content={
            "summary": result_data["summary"],
            "detections": result_data["detections"]
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
    finally:
        # Always clean up the temporary input file
        if os.path.exists(temp_input_path):
            try:
                os.remove(temp_input_path)
            except OSError:
                pass