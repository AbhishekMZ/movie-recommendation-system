import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import NMF, TruncatedSVD
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Comprehensive model evaluation class that combines functionality from multiple evaluation scripts."""
    
    def __init__(self):
        self.metrics_history = []
        self.best_model = None
        self.best_score = float('inf')
    
    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive set of evaluation metrics."""
        metrics = {}
        
        # Basic metrics
        metrics['RMSE'] = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        metrics['MAE'] = float(mean_absolute_error(y_true, y_pred))
        metrics['R2'] = float(r2_score(y_true, y_pred))
        
        # Additional metrics
        residuals = y_true - y_pred
        metrics['MAPE'] = float(np.mean(np.abs(residuals / y_true)) * 100)
        metrics['Within_0.5'] = float(np.mean(np.abs(residuals) <= 0.5) * 100)
        metrics['Within_1.0'] = float(np.mean(np.abs(residuals) <= 1.0) * 100)
        metrics['Bias'] = float(np.mean(residuals))
        metrics['Error_Std'] = float(np.std(residuals))
        
        return metrics
    
    def evaluate_model(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series,
                      content_data: pd.DataFrame = None) -> Dict[str, Any]:
        """Evaluate model performance with detailed metrics and analysis."""
        # Get predictions
        y_pred = model.predict(X_test)
        
        # Calculate basic metrics
        metrics = self.calculate_metrics(y_test, y_pred)
        
        # Add to metrics history
        self.metrics_history.append(metrics)
        
        # Update best model if applicable
        if metrics['RMSE'] < self.best_score:
            self.best_score = metrics['RMSE']
            self.best_model = model
        
        # Add genre-specific metrics if content data is available
        if content_data is not None:
            genre_metrics = self._calculate_genre_metrics(model, X_test, y_test, content_data)
            metrics['Genre_Metrics'] = genre_metrics
        
        return metrics
    
    def _calculate_genre_metrics(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series,
                               content_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate performance metrics for each genre."""
        genre_metrics = {}
        
        # Merge test data with content data to get genres
        test_data = X_test.copy()
        test_data['rating'] = y_test
        test_data = test_data.merge(content_data[['content_id', 'listed_in']], on='content_id')
        
        # Split genres and calculate metrics for each
        for _, row in test_data.iterrows():
            genres = str(row['listed_in']).split(',')
            pred_rating = model.predict(pd.DataFrame({'user_id': [row['user_id']], 
                                                    'content_id': [row['content_id']]}))
            
            for genre in genres:
                genre = genre.strip()
                if genre not in genre_metrics:
                    genre_metrics[genre] = {'true': [], 'pred': []}
                genre_metrics[genre]['true'].append(row['rating'])
                genre_metrics[genre]['pred'].append(pred_rating[0])
        
        # Calculate RMSE for each genre
        return {genre: float(np.sqrt(mean_squared_error(np.array(values['true']), 
                                                      np.array(values['pred']))))
                for genre, values in genre_metrics.items()}
    
    def cross_validate(self, model: Any, data: pd.DataFrame, n_splits: int = 5) -> Dict[str, List[float]]:
        """Perform cross-validation with detailed metrics."""
        cv_metrics = {
            'RMSE': [], 'MAE': [], 'R2': [],
            'Within_0.5': [], 'Within_1.0': [],
            'Bias': [], 'Error_Std': []
        }
        
        for train_idx, test_idx in KFold(n_splits=n_splits, shuffle=True, random_state=42).split(data):
            train_data = data.iloc[train_idx]
            test_data = data.iloc[test_idx]
            
            # Train model
            model.fit(train_data)
            
            # Evaluate
            X_test = test_data[['user_id', 'content_id']]
            y_test = test_data['rating']
            metrics = self.evaluate_model(model, X_test, y_test)
            
            # Store metrics
            for metric, value in metrics.items():
                if metric in cv_metrics:
                    cv_metrics[metric].append(value)
        
        return cv_metrics
    
    def get_similar_items(self, content_id: str, user_item_matrix: pd.DataFrame,
                         n_similar: int = 5) -> List[str]:
        """Find similar items using collaborative filtering."""
        if content_id not in user_item_matrix.columns:
            return []
        
        # Initialize nearest neighbors model
        nn_model = NearestNeighbors(n_neighbors=n_similar+1, metric='cosine')
        nn_model.fit(user_item_matrix.T)  # Transpose for item-item similarity
        
        # Get similar items
        item_idx = list(user_item_matrix.columns).index(content_id)
        distances, indices = nn_model.kneighbors(user_item_matrix.T.iloc[item_idx].values.reshape(1, -1))
        
        # Return similar item IDs (excluding the input item)
        similar_items = [user_item_matrix.columns[idx] for idx in indices[0][1:]]
        return similar_items
    
    def analyze_rating_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze rating patterns and user behavior."""
        analysis = {
            'rating_dist': data['rating'].value_counts().sort_index(),
            'user_stats': {
                'total_users': data['user_id'].nunique(),
                'avg_ratings_per_user': data.groupby('user_id').size().mean(),
                'active_users': data.groupby('user_id').size().quantile(0.9)
            },
            'content_stats': {
                'total_items': data['content_id'].nunique(),
                'avg_ratings_per_item': data.groupby('content_id').size().mean()
            },
            'rating_stats': {
                'mean': data['rating'].mean(),
                'median': data['rating'].median(),
                'std': data['rating'].std()
            }
        }
        return analysis

def evaluate_models(data: pd.DataFrame, models: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Evaluate multiple models and compare their performance."""
    evaluator = ModelEvaluator()
    results = {}
    
    for model_name, model in models.items():
        logger.info(f"Evaluating {model_name}...")
        
        # Split data
        X = data[['user_id', 'content_id']]
        y = data['rating']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        train_data = pd.DataFrame({
            'user_id': X_train['user_id'],
            'content_id': X_train['content_id'],
            'rating': y_train
        })
        model.fit(train_data)
        
        # Evaluate
        metrics = evaluator.evaluate_model(model, X_test, y_test)
        results[model_name] = metrics
        
        logger.info(f"{model_name} - RMSE: {metrics['RMSE']:.4f}, MAE: {metrics['MAE']:.4f}")
    
    return results
