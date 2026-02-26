from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class PersonResult(BaseModel):
    person_id: str
    time_standing_seconds: float
    time_sitting_seconds: float
    time_lying_seconds: float
    time_moving_seconds: float

class VideoAnalysisBase(BaseModel):
    video_id: str
    status: str

class VideoAnalysisCreate(VideoAnalysisBase):
    pass

class VideoAnalysisResponse(VideoAnalysisBase):
    id: int
    analysis_timestamp: datetime
    duration_seconds: int
    people_detected: int
    results: Optional[List[Dict[str, Any]]] = []
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
