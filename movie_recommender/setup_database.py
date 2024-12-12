import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from api.database import Base
from api.schemas import User, Content, Rating, ViewingHistory
import pandas as pd

def setup_database():
    """Set up the database and create initial tables."""
    load_dotenv()
    
    # Create database engine
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Load sample data
    print("\nLoading sample data...")
    data_dir = os.getenv("DATA_DIR", "data")
    
    # Load content data
    content_data = pd.read_csv(os.path.join(data_dir, "content_data.csv"))
    content_data.to_sql("content", engine, if_exists="append", index=False)
    print(f"Loaded {len(content_data)} content items")
    
    # Load viewing history
    viewing_history = pd.read_csv(os.path.join(data_dir, "viewing_history.csv"))
    viewing_history.to_sql("viewing_history", engine, if_exists="append", index=False)
    print(f"Loaded {len(viewing_history)} viewing records")
    
    print("\nDatabase setup completed successfully!")

if __name__ == "__main__":
    setup_database()
