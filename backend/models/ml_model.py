from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from db.database import Base

class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    framework = Column(String, default="yolo") # "yolo", "mediapipe", etc
    is_active = Column(Boolean, default=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
