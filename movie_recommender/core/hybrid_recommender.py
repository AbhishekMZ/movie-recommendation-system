import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import mlflow
import mlflow.sklearn
from typing import List, Dict, Tuple

class HybridRecommender:
    def __init__(self, content_data_path: str, viewing_history_path: str):
        """Initialize the hybrid recommender system."""
        self.content_data = pd.read_csv(content_data_path)
        self.viewing_history = pd.read_csv(viewing_history_path)
        
        # Initialize models
        self.content_similarity = None
        self.collaborative_model = None
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000
        )
    
    def _prepare_content_features(self) -> np.ndarray:
        """Prepare content features using TF-IDF."""
        # Combine relevant text features
        content_features = self.content_data['description'].fillna('') + ' ' + \
                         self.content_data['genres'].fillna('')
        
        # Create TF-IDF matrix
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(content_features)
        return tfidf_matrix
    
    def _prepare_user_item_matrix(self) -> pd.DataFrame:
        """Create user-item interaction matrix."""
        return pd.pivot_table(
            self.viewing_history,
            values='watch_duration',
            index='user_id',
            columns='content_id',
            fill_value=0
        )
    
    def train(self, n_components: int = 100) -> str:
        """Train both content-based and collaborative filtering models."""
        with mlflow.start_run() as run:
            # Log parameters
            mlflow.log_param("n_components", n_components)
            mlflow.log_param("max_features", 5000)
            
            # Content-based filtering
            print("Training content-based model...")
            tfidf_matrix = self._prepare_content_features()
            self.content_similarity = cosine_similarity(tfidf_matrix)
            
            # Collaborative filtering
            print("Training collaborative filtering model...")
            user_item_matrix = self._prepare_user_item_matrix()
            self.collaborative_model = TruncatedSVD(n_components=n_components)
            user_item_transformed = self.collaborative_model.fit_transform(user_item_matrix)
            
            # Log metrics
            explained_variance = self.collaborative_model.explained_variance_ratio_.sum()
            mlflow.log_metric("explained_variance", explained_variance)
            
            # Save models
            mlflow.sklearn.log_model(
                self.collaborative_model,
                "collaborative_model"
            )
            
            return run.info.run_id
    
    def get_content_based_recommendations(
        self,
        content_id: str,
        n_recommendations: int = 10
    ) -> List[Tuple[str, float]]:
        """Get content-based recommendations."""
        if self.content_similarity is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Get the index of the content
        idx = self.content_data[
            self.content_data['content_id'] == content_id
        ].index[0]
        
        # Get similarity scores
        sim_scores = list(enumerate(self.content_similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:n_recommendations+1]
        
        # Get content indices and scores
        content_indices = [i[0] for i in sim_scores]
        similarity_scores = [i[1] for i in sim_scores]
        
        return list(zip(
            self.content_data.iloc[content_indices]['content_id'],
            similarity_scores
        ))
    
    def get_collaborative_recommendations(
        self,
        user_id: str,
        n_recommendations: int = 10
    ) -> List[Tuple[str, float]]:
        """Get collaborative filtering recommendations."""
        if self.collaborative_model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Get user's viewing history
        user_history = self.viewing_history[
            self.viewing_history['user_id'] == user_id
        ]
        
        # Create user vector
        user_vector = pd.Series(
            user_history['watch_duration'].values,
            index=user_history['content_id']
        )
        
        # Transform user vector
        user_transformed = self.collaborative_model.transform([user_vector])
        
        # Get recommendations
        user_item_matrix = self._prepare_user_item_matrix()
        all_content_transformed = self.collaborative_model.transform(user_item_matrix)
        
        # Calculate similarities
        similarities = cosine_similarity(
            user_transformed,
            all_content_transformed
        )[0]
        
        # Get top recommendations
        content_ids = user_item_matrix.columns
        recommendations = list(zip(content_ids, similarities))
        recommendations = sorted(
            recommendations,
            key=lambda x: x[1],
            reverse=True
        )
        
        # Filter out already watched content
        watched_content = set(user_history['content_id'])
        recommendations = [
            (content_id, score)
            for content_id, score in recommendations
            if content_id not in watched_content
        ]
        
        return recommendations[:n_recommendations]
    
    def get_hybrid_recommendations(
        self,
        user_id: str,
        content_weight: float = 0.3,
        n_recommendations: int = 10
    ) -> List[Dict[str, any]]:
        """Get hybrid recommendations combining both approaches."""
        # Get recommendations from both models
        collaborative_recs = self.get_collaborative_recommendations(
            user_id,
            n_recommendations=n_recommendations
        )
        
        # Get a recently watched item for content-based recommendations
        recent_watch = self.viewing_history[
            self.viewing_history['user_id'] == user_id
        ].sort_values('timestamp', ascending=False).iloc[0]
        
        content_recs = self.get_content_based_recommendations(
            recent_watch['content_id'],
            n_recommendations=n_recommendations
        )
        
        # Combine recommendations
        content_dict = dict(content_recs)
        collab_dict = dict(collaborative_recs)
        all_content_ids = set(content_dict.keys()) | set(collab_dict.keys())
        
        hybrid_scores = {}
        for content_id in all_content_ids:
            content_score = content_dict.get(content_id, 0)
            collab_score = collab_dict.get(content_id, 0)
            
            # Calculate hybrid score
            hybrid_scores[content_id] = (
                content_weight * content_score +
                (1 - content_weight) * collab_score
            )
        
        # Sort and get top recommendations
        recommendations = sorted(
            hybrid_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n_recommendations]
        
        # Add content details
        result = []
        for content_id, score in recommendations:
            content_info = self.content_data[
                self.content_data['content_id'] == content_id
            ].iloc[0]
            
            result.append({
                'content_id': content_id,
                'title': content_info['title'],
                'predicted_rating': min(5.0, score * 5),  # Scale to 5-star rating
                'confidence': score
            })
        
        return result
