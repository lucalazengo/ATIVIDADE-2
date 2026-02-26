from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from db.database import Base

class VideoAnalysis(Base):
    __tablename__ = "video_analyses"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True, nullable=False) # e.g. "video_2025_05..."
    status = Column(String, default="pending") # "pending", "processing", "completed", "failed"
    analysis_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    duration_seconds = Column(Integer, default=0)
    people_detected = Column(Integer, default=0)
    
    # Store complete JSON results
    results = Column(JSON, nullable=True)
    
    error_message = Column(String, nullable=True)
