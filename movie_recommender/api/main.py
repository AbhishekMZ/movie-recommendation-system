from fastapi import FastAPI, HTTPException, Depends, status
from typing import List, Optional
import mlflow
from pathlib import Path
from core.hybrid_recommender import HybridRecommender

from .models import (
    UserCreate,
    UserLogin,
    User,
    ContentItem,
    Rating,
    RecommendationRequest,
    RecommendationResponse,
    Token
)
from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    setup_cors,
    setup_security,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from .database import SessionLocal, engine
from . import crud, schemas
from datetime import timedelta

# Create FastAPI app
app = FastAPI(
    title="Movie Recommender API",
    description="A secure API for movie recommendations",
    version="1.0.0"
)

# Set up security
setup_cors(app)
setup_security(app)

# Initialize recommender
recommender = HybridRecommender(
    content_data_path="data/content_data.csv",
    viewing_history_path="data/viewing_history.csv"
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=User)
async def create_user(user: UserCreate, db=Depends(get_db)):
    """Create a new user."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)

@app.post("/token", response_model=Token)
async def login(user_data: UserLogin, db=Depends(get_db)):
    """Login and get access token."""
    user = crud.get_user_by_email(db, email=user_data.email)
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(verify_token),
    db=Depends(get_db)
):
    """Get current user information."""
    return current_user

@app.get("/recommendations/", response_model=List[RecommendationResponse])
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(verify_token),
    db=Depends(get_db)
):
    """Get personalized content recommendations."""
    try:
        recommendations = recommender.get_hybrid_recommendations(
            user_id=current_user.id,
            content_weight=0.3,
            n_recommendations=request.limit or 10
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )

@app.post("/ratings/", response_model=Rating)
async def create_rating(
    rating: Rating,
    current_user: User = Depends(verify_token),
    db=Depends(get_db)
):
    """Submit a rating for content."""
    return crud.create_rating(db=db, rating=rating, user_id=current_user.id)

@app.get("/content/", response_model=List[ContentItem])
async def get_content(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(verify_token),
    db=Depends(get_db)
):
    """Get a list of content items."""
    return crud.get_content(db, skip=skip, limit=limit)

@app.get("/content/{content_id}", response_model=ContentItem)
async def get_content_item(
    content_id: str,
    current_user: User = Depends(verify_token),
    db=Depends(get_db)
):
    """Get details for a specific content item."""
    content = crud.get_content_item(db, content_id=content_id)
    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    return content
