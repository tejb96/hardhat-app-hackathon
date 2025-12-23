from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from PIL import Image
from io import BytesIO
import tempfile
import uuid
import os
from ..services.cv import detect_objects
from ..services.report_generation import generate_pdf_report

router = APIRouter(prefix="/detection", tags=["PPE Detection"])

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_FILESIZE = 10 * 1024 * 1024

TEMP_DIR = os.path.join(tempfile.gettempdir(), "ppe_sessions")
os.makedirs(TEMP_DIR, exist_ok=True)


def cleanup_session(session_dir: str):
    if os.path.exists(session_dir):
        for file in os.listdir(session_dir):
            try:
                os.remove(os.path.join(session_dir, file))
            except OSError:
                pass
        try:
            os.rmdir(session_dir)
        except OSError:
            pass


@router.post("/detect")
async def detect(file: UploadFile = File(...)):
    filename = file.filename or "uploaded_image"
    extension = os.path.splitext(filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    contents = await file.read()
    if len(contents) > ALLOWED_FILESIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

    try:
        Image.open(BytesIO(contents)).verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image.")

    session_id = str(uuid.uuid4())
    session_dir = os.path.join(TEMP_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    original_path = os.path.join(session_dir, f"original{extension}")
    annotated_path = os.path.join(session_dir, f"annotated{extension}")

    try:
        with open(original_path, "wb") as f:
            f.write(contents)

        # This now saves the annotated image
        result_data = detect_objects(original_path, output_image_path=annotated_path)

        return JSONResponse(content={
            "session_id": session_id,
            "annotated_image_url": f"/detection/annotated/{session_id}{extension}",
            "summary": result_data["summary"],
            "detections": result_data["detections"]
        })

    except Exception as e:
        cleanup_session(session_dir)
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.get("/annotated/{session_id}{extension:path}")
async def get_annotated_image(session_id: str, extension: str):
    path = os.path.join(TEMP_DIR, session_id, f"annotated{extension}")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found or expired.")
    return FileResponse(path, media_type="image/jpeg")


@router.post("/generate-report/{session_id}")
async def generate_report(session_id: str, background_tasks: BackgroundTasks):
    session_dir = os.path.join(TEMP_DIR, session_id)
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="Session not found.")

    files = os.listdir(session_dir)
    original_path = next((os.path.join(session_dir, f) for f in files if f.startswith("original")), None)
    annotated_path = next((os.path.join(session_dir, f) for f in files if f.startswith("annotated")), None)

    if not original_path or not annotated_path:
        raise HTTPException(status_code=500, detail="Required images missing.")

    report_path = os.path.join(session_dir, "ppe_report.pdf")

    try:
        generate_pdf_report(original_path, annotated_path, report_path)
        background_tasks.add_task(cleanup_session, session_dir)

        return FileResponse(
            report_path,
            media_type="application/pdf",
            filename="ppe_safety_report.pdf"
        )
    except Exception as e:
        if os.path.exists(report_path):
            os.remove(report_path)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")