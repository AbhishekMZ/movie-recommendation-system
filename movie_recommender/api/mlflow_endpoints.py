from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
import mlflow
from ..core.recommender import MovieRecommender
from .security import verify_token
from .models import User, TrainingResponse, ModelInfo
import pandas as pd

router = APIRouter()
recommender = MovieRecommender()

@router.post("/train", response_model=TrainingResponse)
async def train_model(current_user: User = Depends(verify_token)):
    """Train the recommendation model and log with MLflow"""
    try:
        # Load data (in production, this would come from your database)
        ratings_df = pd.read_csv("data/ratings.csv")
        movies_df = pd.read_csv("data/movies.csv")
        
        # Set MLflow tracking URI (use local directory for simplicity)
        mlflow.set_tracking_uri("file:./mlruns")
        
        # Train model
        recommender.train(ratings_df, movies_df)
        
        # Get the current run ID
        run_id = mlflow.active_run().info.run_id
        
        return {
            "status": "success",
            "message": "Model trained successfully",
            "run_id": run_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error training model: {str(e)}"
        )

@router.get("/models", response_model=List[ModelInfo])
async def list_models(current_user: User = Depends(verify_token)):
    """List all trained models"""
    try:
        # Set MLflow tracking URI
        mlflow.set_tracking_uri("file:./mlruns")
        
        # Get all runs
        client = mlflow.tracking.MlflowClient()
        runs = client.search_runs(
            experiment_ids=["0"],
            order_by=["attribute.start_time DESC"]
        )
        
        models = []
        for run in runs:
            models.append({
                "run_id": run.info.run_id,
                "start_time": run.info.start_time,
                "metrics": run.data.metrics,
                "parameters": run.data.params
            })
        
        return models
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing models: {str(e)}"
        )

@router.post("/models/{run_id}/load")
async def load_model(run_id: str, current_user: User = Depends(verify_token)):
    """Load a specific model version"""
    try:
        success = recommender.load_model(run_id)
        if success:
            return {"status": "success", "message": f"Model {run_id} loaded successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to load model"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading model: {str(e)}"
        )
