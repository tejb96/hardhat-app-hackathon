from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from PIL import Image
from io import BytesIO
import tempfile
import uuid
import os
import json
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

        # Save detection results to a JSON file in the session directory for later use
        results_file = os.path.join(session_dir, "detection_results.json")
        with open(results_file, "w") as f:
            json.dump(result_data, f)

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
    print(f"[DEBUG] Attempting to generate report for session: {session_id}")
    print(f"[DEBUG] Session dir path: {session_dir}")
    print(f"[DEBUG] Session dir exists: {os.path.exists(session_dir)}")
    
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail=f"Session not found: {session_dir}")

    files = os.listdir(session_dir)
    print(f"[DEBUG] Files in session: {files}")
    
    original_path = next((os.path.join(session_dir, f) for f in files if f.startswith("original")), None)
    annotated_path = next((os.path.join(session_dir, f) for f in files if f.startswith("annotated")), None)

    print(f"[DEBUG] Original path: {original_path}")
    print(f"[DEBUG] Annotated path: {annotated_path}")

    if not original_path or not annotated_path:
        raise HTTPException(status_code=500, detail="Required images missing.")

    # Load detection results from JSON file
    results_file = os.path.join(session_dir, "detection_results.json")
    summary = None
    detections = None
    
    if os.path.exists(results_file):
        try:
            with open(results_file, "r") as f:
                result_data = json.load(f)
                summary = result_data.get("summary")
                detections = result_data.get("detections")
                print(f"[DEBUG] Loaded results: {summary}")
        except Exception as e:
            print(f"Warning: Could not load detection results: {e}")

    report_path = os.path.join(session_dir, "ppe_report.pdf")

    try:
        print(f"[DEBUG] Generating report at: {report_path}")
        generate_pdf_report(
            original_path, 
            annotated_path, 
            report_path,
            summary=summary,
            detections=detections
        )
        print(f"[DEBUG] Report generated successfully")
        
        # Read the PDF file into memory to avoid cleanup issues
        with open(report_path, "rb") as f:
            pdf_content = f.read()
        
        print(f"[DEBUG] PDF read into memory, size: {len(pdf_content)} bytes")
        
        # Schedule cleanup after file is read
        background_tasks.add_task(cleanup_session, session_dir)

        return FileResponse(
            report_path,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=ppe_safety_report.pdf"}
        )
    except Exception as e:
        print(f"[ERROR] Report generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        if os.path.exists(report_path):
            os.remove(report_path)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")