import os
from dotenv import load_dotenv
from pathlib import Path
import mlflow
from core.mlflow_recommender import MLflowRecommender

def test_mlflow_deployment():
    """Test MLflow model training, tracking, and deployment."""
    
    # Load environment variables
    load_dotenv()
    
    # Set up paths
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    content_data_path = str(data_dir / "content_data.csv")
    viewing_history_path = str(data_dir / "viewing_history.csv")
    
    # Initialize recommender
    print("Initializing MLflow recommender...")
    recommender = MLflowRecommender(content_data_path, viewing_history_path)
    
    # Train model with MLflow tracking
    print("\nTraining model with MLflow tracking...")
    run_id = recommender.train(n_components=100)
    print(f"Training completed. Run ID: {run_id}")
    
    # Load model from MLflow
    print("\nLoading model from MLflow...")
    loaded_recommender = MLflowRecommender(content_data_path, viewing_history_path)
    loaded_recommender.load_model(run_id)
    
    # Test recommendations
    print("\nTesting recommendations...")
    test_user = "USR_001"
    test_content = ["AMZ_001", "AMZ_002", "NFX_001"]
    
    predictions = loaded_recommender.calculate_expected_ratings(test_user, test_content)
    print("\nPredicted ratings:")
    for content_id, rating in predictions.items():
        print(f"{content_id}: {rating:.2f}")
    
    # Print MLflow tracking info
    print("\nMLflow tracking information:")
    print(f"Tracking URI: {mlflow.get_tracking_uri()}")
    print(f"Current experiment: {mlflow.get_experiment(recommender.experiment.experiment_id).name}")

if __name__ == "__main__":
    test_mlflow_deployment()
