import os
import shutil
import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from core.deps import get_current_user
from crud import video_analysis as crud_video
from db.database import get_db
from models.user import User
from schemas.video_analysis import VideoAnalysisResponse

router = APIRouter()

VIDEOS_DIR = os.getenv("VIDEOS_DIR", "./videos")

@router.post("/upload", response_model=VideoAnalysisResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    # Descomente abaixo para forçar autenticação:
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Upload a video file to be processed by the ML Pipeline.
    """
    if not os.path.exists(VIDEOS_DIR):
        os.makedirs(VIDEOS_DIR)

    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["mp4", "avi", "mov", "mkv"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid format. Please upload a .mp4, .avi, .mov, or .mkv file."
        )

    video_id = f"video_{uuid.uuid4().hex[:12]}_{file.filename}"
    file_path = os.path.join(VIDEOS_DIR, video_id)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. Create a "processing" record
    record = crud_video.create_analysis_record(db, video_id=video_id)
    
    # 2. Trigger asynchronous processing via OpenCV/YOLO
    background_tasks.add_task(crud_video.process_video_background, file_path, video_id, db)
    
    return record


@router.get("/", response_model=List[VideoAnalysisResponse])
def list_video_analyses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    List all previously requested analyses.
    """
    return crud_video.get_all_analyses(db, skip=skip, limit=limit)


@router.get("/{video_id}/results", response_model=VideoAnalysisResponse)
def get_video_results(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get the analysis results formatted exactly as requested.
    """
    analysis = crud_video.get_analysis(db, video_id=video_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Video analysis not found")
        
    # The response_model dict structure automatically maps the SQL JSON column
    return analysis
