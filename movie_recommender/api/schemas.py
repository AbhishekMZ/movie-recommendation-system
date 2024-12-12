from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ratings = relationship("Rating", back_populates="user")
    viewing_history = relationship("ViewingHistory", back_populates="user")

class Content(Base):
    __tablename__ = "content"

    content_id = Column(String, primary_key=True, index=True)
    title = Column(String)
    type = Column(String)
    description = Column(String, nullable=True)
    release_date = Column(DateTime, nullable=True)
    genres = Column(ARRAY(String))
    
    ratings = relationship("Rating", back_populates="content")
    viewing_history = relationship("ViewingHistory", back_populates="content")

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(String, ForeignKey("content.content_id"))
    rating = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="ratings")
    content = relationship("Content", back_populates="ratings")

class ViewingHistory(Base):
    __tablename__ = "viewing_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(String, ForeignKey("content.content_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    watch_duration = Column(Integer)  # Duration in seconds
    
    user = relationship("User", back_populates="viewing_history")
    content = relationship("Content", back_populates="viewing_history")
