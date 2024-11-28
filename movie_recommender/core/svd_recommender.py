import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging
import time
from pathlib import Path
from scipy.sparse import csr_matrix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SVDRecommender:
    def __init__(self, n_components=100, random_state=42):
        """Initialize SVD recommender with given number of components."""
        self.n_components = n_components
        self.random_state = random_state
        self.svd = TruncatedSVD(n_components=n_components, random_state=random_state)
        self.scaler = StandardScaler(with_mean=False)  # Sparse matrix friendly
        self.user_item_matrix = None
        self.user_features = None
        self.item_features = None
        self.mean_rating = None
        self.rating_std = None
        self.global_mean = 0
        self.user_biases = {}
        self.item_biases = {}

    def _create_user_item_matrix(self, ratings_df):
        """Create sparse user-item matrix efficiently."""
        ratings_df = ratings_df.copy()
        ratings_df['rating'] = pd.to_numeric(ratings_df['rating'], errors='coerce')
        ratings_df = ratings_df.dropna(subset=['rating'])

        # Compute mean and standard deviation for normalization
        self.mean_rating = ratings_df['rating'].mean()
        self.rating_std = ratings_df['rating'].std()

        # Encode user and item IDs
        user_ids = pd.factorize(ratings_df['user_id'])[0]
        item_ids = pd.factorize(ratings_df['content_id'])[0]

        self.user_map = dict(enumerate(ratings_df['user_id'].unique()))
        self.item_map = dict(enumerate(ratings_df['content_id'].unique()))
        self.reverse_user_map = {v: k for k, v in self.user_map.items()}
        self.reverse_item_map = {v: k for k, v in self.item_map.items()}

        # Create sparse user-item matrix
        self.user_item_matrix = csr_matrix(
            (ratings_df['rating'].values, (user_ids, item_ids))
        )
        return self.user_item_matrix

    def _compute_biases(self, ratings_df):
        """Compute user and item biases."""
        self.global_mean = float(ratings_df['rating'].mean())
        
        # Compute user biases
        user_means = ratings_df.groupby('user_id')['rating'].mean()
        self.user_biases = (user_means - self.global_mean).to_dict()
        
        # Compute item biases
        residuals = ratings_df['rating'] - ratings_df['user_id'].map(self.user_biases) - self.global_mean
        item_means = residuals.groupby(ratings_df['content_id']).mean()
        self.item_biases = item_means.to_dict()

    def fit(self, ratings_df):
        """Train the SVD model on rating data."""
        logger.info("Creating user-item matrix...")
        start_time = time.time()
        X = self._create_user_item_matrix(ratings_df)

        # Normalize data
        X_scaled = self.scaler.fit_transform(X)

        # Fit SVD
        logger.info("Training SVD model...")
        self.user_features = self.svd.fit_transform(X_scaled)
        self.item_features = self.svd.components_.T

        explained_var = self.svd.explained_variance_ratio_.sum()
        train_time = time.time() - start_time
        logger.info(f"Model explains {explained_var:.1%} of the variance")
        logger.info(f"Training completed in {train_time:.2f} seconds")

        # Compute biases
        self._compute_biases(ratings_df)

    def predict(self, user_id, content_id):
        """Predict rating for a specific user-item pair."""
        try:
            user_idx = self.reverse_user_map.get(user_id)
            item_idx = self.reverse_item_map.get(content_id)
            
            if user_idx is None or item_idx is None:
                # Cold start: return global mean
                return self.global_mean
            
            # Get latent features
            user_vec = self.user_features[user_idx].reshape(1, -1)
            item_vec = self.item_features[item_idx].reshape(-1, 1)
            
            # Compute base prediction from SVD
            base_pred = np.dot(user_vec, item_vec)[0][0]
            
            # Add biases
            prediction = (
                base_pred +
                self.global_mean +
                self.user_biases.get(user_id, 0) +
                self.item_biases.get(content_id, 0)
            )
            
            # Clip to valid rating range
            return float(np.clip(prediction, 1, 5))
            
        except Exception as e:
            logger.warning(f"Error predicting rating: {str(e)}")
            return float(self.global_mean)

    def recommend_for_user(self, user_id, n_recommendations=5):
        """Generate recommendations for a specific user."""
        if user_id not in self.reverse_user_map:
            return pd.DataFrame(columns=['content_id', 'predicted_rating'])

        user_idx = self.reverse_user_map[user_id]
        user_vector = self.user_features[user_idx]

        predicted_ratings = np.dot(user_vector, self.item_features.T)
        predicted_ratings = self.scaler.inverse_transform(predicted_ratings.reshape(1, -1)).flatten()

        recommendations = pd.DataFrame({
            'content_id': list(self.item_map.values()),
            'predicted_rating': predicted_ratings
        }).sort_values('predicted_rating', ascending=False).head(n_recommendations)

        return recommendations

def evaluate_model(data, test_size=0.2, random_state=42):
    """Evaluate the model and calculate accuracy metrics."""
    data['rating'] = pd.to_numeric(data['rating'], errors='coerce')
    data = data.dropna(subset=['rating'])

    train_data, test_data = train_test_split(data, test_size=test_size, random_state=random_state)

    # Train the model
    model = SVDRecommender()
    model.fit(train_data)

    # Predict ratings for the test set
    y_true, y_pred = [], []
    for _, row in test_data.iterrows():
        y_true.append(row['rating'])
        y_pred.append(model.predict(row['user_id'], row['content_id']))

    # Evaluate metrics
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    logger.info(f"RMSE: {rmse:.3f}")
    logger.info(f"MAE: {mae:.3f}")
    logger.info(f"R²: {r2:.3f}")

    return {'rmse': rmse, 'mae': mae, 'r2': r2}

def main():
    try:
        # Load data
        data_path = Path(__file__).parent.parent / "data" / "viewing_history.csv"
        data = pd.read_csv(data_path)

        # Evaluate the model
        metrics = evaluate_model(data)
        logger.info(f"Evaluation Metrics: {metrics}")
    except Exception as e:
        logger.error(f"Error in recommendation system: {str(e)}")

if __name__ == "__main__":
    main()
