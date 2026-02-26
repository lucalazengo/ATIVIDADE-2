import os
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from ml_pipeline.vision_core import PoseEstimator
from models.video_analysis import VideoAnalysis
from schemas.video_analysis import VideoAnalysisCreate
from crud.ml_model import get_active_model

def get_analysis(db: Session, video_id: str):
    return db.query(VideoAnalysis).filter(VideoAnalysis.video_id == video_id).first()

def get_all_analyses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(VideoAnalysis).order_by(VideoAnalysis.analysis_timestamp.desc()).offset(skip).limit(limit).all()

def create_analysis_record(db: Session, video_id: str):
    db_obj = VideoAnalysis(
        video_id=video_id,
        status="processing"
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_analysis_status(db: Session, video_id: str, status: str, error_message: str = None, results: dict = None, duration: int = None, people: int = None):
    obj = db.query(VideoAnalysis).filter(VideoAnalysis.video_id == video_id).first()
    if obj:
        obj.status = status
        obj.error_message = error_message
        if results:
            obj.results = results
        if duration:
            obj.duration_seconds = duration
        if people is not None:
            obj.people_detected = people
            
        db.commit()
        db.refresh(obj)
    return obj


# Background worker function
def process_video_background(video_path: str, video_id: str, db: Session):
    try:
        active_model = get_active_model(db)
        # Choose framework
        framework = active_model.framework if active_model else "yolo"
        model_name = active_model.filename if active_model else "yolov8n-pose.pt"
        
        # In a real environment, prefix model_name with the models/ directory path
        model_path = os.path.join(os.getenv("MODELS_DIR", "./models"), model_name)
        if not os.path.exists(model_path):
            # Fallback to YOLO lightweight default if model file missing
            model_path = "yolov8n-pose.pt"
        
        estimator = PoseEstimator(model_path=model_path, framework=framework)
        
        # Execute long computation
        data = estimator.process_video(video_path)
        
        # Success
        update_analysis_status(
            db, 
            video_id=video_id, 
            status="completed",
            results=data["results"],
            duration=data["duration_seconds"],
            people=data["people_detected"]
        )
        
    except Exception as e:
        update_analysis_status(
            db, 
            video_id=video_id, 
            status="failed", 
            error_message=str(e)
        )
