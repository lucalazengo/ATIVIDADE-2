import os
import shutil
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from core.deps import get_current_user
from crud import ml_model as crud_ml_model
from db.database import get_db
from models.user import User
from schemas.ml_model import MLModelCreate, MLModelResponse

router = APIRouter()

MODELS_DIR = os.getenv("MODELS_DIR", "./models")

@router.post("/upload", response_model=MLModelResponse)
async def upload_model(
    file: UploadFile = File(...),
    description: str = Form(None),
    framework: str = Form("yolo"),
    set_active: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Upload a new trained model file (.pt, .pkl).
    This endpoint automatically activates the latest uploaded model if set_active is True.
    """
    # Create the directory if it doesn't exist
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)

    file_extension = file.filename.split(".")[-1]
    if file_extension not in ["pt", "pkl", "onnx", "h5", "tflite"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file format. Please upload .pt, .pkl, .onnx, .h5, or .tflite weights."
        )

    # To avoid filename collisions, we could hash or timestamp it, but we'll keep original for simplicity
    file_path = os.path.join(MODELS_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    model_in = MLModelCreate(
        filename=file.filename,
        description=description,
        framework=framework,
        is_active=set_active
    )
    
    return crud_ml_model.create_model_record(db, model_create=model_in)

@router.get("/", response_model=List[MLModelResponse])
def get_models(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    List all uploaded models history
    """
    return crud_ml_model.get_models(db, skip=skip, limit=limit)


@router.put("/{model_id}/activate", response_model=MLModelResponse)
def activate_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Set a specific model as the active framework for Video Inference
    """
    model = crud_ml_model.set_model_active(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@router.get("/active", response_model=MLModelResponse)
def get_current_active_model(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get the currently active ML model configured in the DB
    """
    model = crud_ml_model.get_active_model(db)
    if not model:
        raise HTTPException(status_code=404, detail="No active machine learning model set in the system.")
    return model
