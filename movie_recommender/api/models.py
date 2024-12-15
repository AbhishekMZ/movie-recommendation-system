from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ContentItem(BaseModel):
    content_id: str
    title: str
    type: str
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    genres: List[str] = []
    
    class Config:
        from_attributes = True

class Rating(BaseModel):
    content_id: str
    rating: float
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class RecommendationRequest(BaseModel):
    limit: Optional[int] = 10

class RecommendationResponse(BaseModel):
    content_id: str
    title: str
    predicted_rating: float
    confidence: Optional[float] = None
    
    class Config:
        from_attributes = True

class TrainingResponse(BaseModel):
    status: str
    message: str
    run_id: str

class ModelInfo(BaseModel):
    run_id: str
    start_time: int
    metrics: Dict[str, float]
    parameters: Dict[str, str]

class ModelLoadResponse(BaseModel):
    status: str
    message: str
