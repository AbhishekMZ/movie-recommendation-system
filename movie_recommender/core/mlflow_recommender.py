import mlflow
import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
from pathlib import Path

from .streaming_recommender import StreamingRecommender
from ..mlflow_config import setup_mlflow, REGISTERED_MODEL_NAME

class MLflowRecommender(StreamingRecommender):
    """Enhanced recommender with MLflow tracking."""
    
    def __init__(self, content_data_path: str, viewing_history_path: str):
        super().__init__(content_data_path, viewing_history_path)
        self.experiment = setup_mlflow()
        
    def train(self, n_components=100):
        """Train the recommendation model with MLflow tracking."""
        with mlflow.start_run(experiment_id=self.experiment.experiment_id) as run:
            # Log parameters
            mlflow.log_param("n_components", n_components)
            mlflow.log_param("content_data_size", len(self.content_data))
            mlflow.log_param("viewing_history_size", len(self.viewing_history))
            
            # Create user-item matrix
            print("Creating user-item matrix...")
            user_item_matrix = self._create_user_item_matrix()
            
            # Train SVD model
            print("Training SVD model...")
            self.svd_model = TruncatedSVD(n_components=n_components)
            user_item_transformed = self.svd_model.fit_transform(user_item_matrix)
            
            # Log metrics
            explained_variance = self.svd_model.explained_variance_ratio_.sum() * 100
            mlflow.log_metric("explained_variance_percentage", explained_variance)
            print(f"Model explains {explained_variance:.1f}% of the variance")
            
            # Save artifacts
            model_path = Path("artifacts") / "svd_model.joblib"
            mlflow.sklearn.save_model(
                self.svd_model,
                model_path,
                registered_model_name=REGISTERED_MODEL_NAME
            )
            
            # Log additional metrics
            self._log_model_evaluation_metrics()
            
            return run.info.run_id
            
    def _log_model_evaluation_metrics(self):
        """Log evaluation metrics for the model."""
        # Sample users for evaluation
        sample_users = np.random.choice(
            self.viewing_history['user_id'].unique(),
            size=min(50, len(self.viewing_history['user_id'].unique())),
            replace=False
        )
        
        mae_scores = []
        rmse_scores = []
        
        for user_id in sample_users:
            # Get actual ratings
            user_history = self.viewing_history[self.viewing_history['user_id'] == user_id]
            content_ids = user_history['content_id'].tolist()
            
            # Get predicted ratings
            predicted_ratings = self.calculate_expected_ratings(user_id, content_ids)
            
            # Calculate errors
            actual_ratings = [4.0] * len(content_ids)  # Assuming target rating of 4.0
            predicted = [predicted_ratings[cid] for cid in content_ids]
            
            # Calculate metrics
            mae = np.mean(np.abs(np.array(actual_ratings) - np.array(predicted)))
            rmse = np.sqrt(np.mean((np.array(actual_ratings) - np.array(predicted))**2))
            
            mae_scores.append(mae)
            rmse_scores.append(rmse)
        
        # Log average metrics
        mlflow.log_metric("mean_absolute_error", np.mean(mae_scores))
        mlflow.log_metric("root_mean_squared_error", np.mean(rmse_scores))
    
    def load_model(self, run_id):
        """Load a model from MLflow tracking."""
        model_path = f"runs:/{run_id}/artifacts/svd_model"
        self.svd_model = mlflow.sklearn.load_model(model_path)
        return self
