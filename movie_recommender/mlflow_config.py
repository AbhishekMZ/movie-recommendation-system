import os
from pathlib import Path

# MLflow tracking configuration
MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"
EXPERIMENT_NAME = "movie_recommender"

# Model registry configuration
MODEL_REGISTRY_PATH = str(Path(__file__).parent / "model_registry")
REGISTERED_MODEL_NAME = "movie_recommender_model"

# Artifact paths
ARTIFACTS_PATH = str(Path(__file__).parent / "artifacts")

def setup_mlflow():
    """Setup MLflow tracking and create necessary directories."""
    import mlflow
    
    # Set tracking URI
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    # Create directories if they don't exist
    os.makedirs(MODEL_REGISTRY_PATH, exist_ok=True)
    os.makedirs(ARTIFACTS_PATH, exist_ok=True)
    
    # Create or get experiment
    try:
        experiment = mlflow.create_experiment(
            EXPERIMENT_NAME,
            artifact_location=ARTIFACTS_PATH
        )
    except Exception:
        experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    
    return experiment
