from datetime import datetime
from pydantic import BaseModel

class MLModelBase(BaseModel):
    description: str | None = None
    framework: str | None = "yolo" 

class MLModelCreate(MLModelBase):
    filename: str
    is_active: bool = False

class MLModelResponse(MLModelBase):
    id: int
    filename: str
    is_active: bool
    upload_date: datetime

    class Config:
        from_attributes = True
