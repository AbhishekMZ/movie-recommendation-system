from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from . import models, schemas
from .auth import get_password_hash

def get_user(db: Session, user_id: int) -> Optional[schemas.User]:
    """Get user by ID."""
    return db.query(schemas.User).filter(schemas.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[schemas.User]:
    """Get user by email."""
    return db.query(schemas.User).filter(schemas.User.email == email).first()

def create_user(db: Session, user: models.UserCreate) -> schemas.User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = schemas.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_content(
    db: Session,
    skip: int = 0,
    limit: int = 10
) -> List[schemas.Content]:
    """Get list of content items."""
    return db.query(schemas.Content).offset(skip).limit(limit).all()

def get_content_item(
    db: Session,
    content_id: str
) -> Optional[schemas.Content]:
    """Get specific content item."""
    return db.query(schemas.Content).filter(
        schemas.Content.content_id == content_id
    ).first()

def create_rating(
    db: Session,
    rating: models.Rating,
    user_id: int
) -> schemas.Rating:
    """Create a new rating."""
    db_rating = schemas.Rating(
        user_id=user_id,
        content_id=rating.content_id,
        rating=rating.rating,
        timestamp=datetime.utcnow()
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

def get_recommendations(
    db: Session,
    model,
    user_id: int,
    limit: int = 10
) -> List[models.RecommendationResponse]:
    """Get personalized recommendations using the ML model."""
    # Get user's viewing history
    user_history = db.query(schemas.ViewingHistory).filter(
        schemas.ViewingHistory.user_id == user_id
    ).all()
    
    # Get all content
    all_content = db.query(schemas.Content).all()
    
    # Filter out already watched content
    watched_ids = {h.content_id for h in user_history}
    unwatched_content = [c for c in all_content if c.content_id not in watched_ids]
    
    # Get predictions for unwatched content
    predictions = []
    for content in unwatched_content:
        # Use the model to predict rating
        predicted_rating = model.predict(user_id, content.content_id)
        predictions.append({
            'content_id': content.content_id,
            'title': content.title,
            'predicted_rating': predicted_rating,
            'confidence': 0.8  # Placeholder for now
        })
    
    # Sort by predicted rating and return top N
    predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
    return predictions[:limit]
