from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    ratings = relationship("Rating", back_populates="user")

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    genres = Column(String)
    
    ratings = relationship("Rating", back_populates="movie")

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    rating = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")
