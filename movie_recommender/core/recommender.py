import mlflow
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split

class MovieRecommender:
    def __init__(self):
        self.model_name = "movie_recommender"
        self.svd_model = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.movies_df = None
        
    def train(self, ratings_df, movies_df):
        """Train the recommendation model and log with MLflow"""
        with mlflow.start_run(run_name="movie_recommender_training"):
            # Log parameters
            mlflow.log_param("n_factors", 100)
            mlflow.log_param("n_epochs", 20)
            
            # Train SVD model
            reader = Reader(rating_scale=(1, 5))
            data = Dataset.load_from_df(ratings_df[["user_id", "movie_id", "rating"]], reader)
            trainset = data.build_full_trainset()
            
            self.svd_model = SVD(n_factors=100, n_epochs=20)
            self.svd_model.fit(trainset)
            
            # Train content-based model
            self.movies_df = movies_df
            self.tfidf_vectorizer = TfidfVectorizer(stop_words="english")
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(movies_df["genres"].fillna(""))
            
            # Log metrics
            mlflow.log_metric("training_size", len(ratings_df))
            mlflow.log_metric("n_users", len(ratings_df["user_id"].unique()))
            mlflow.log_metric("n_movies", len(movies_df))
            
            # Save models
            mlflow.sklearn.log_model(self.tfidf_vectorizer, "tfidf_vectorizer")
            mlflow.pyfunc.log_model("svd_model", python_model=self.svd_model)
    
    def get_recommendations(self, user_id, n_recommendations=5):
        """Get hybrid recommendations for a user"""
        if not self.svd_model or not self.tfidf_matrix.any():
            raise ValueError("Model not trained")
        
        # Get all movie IDs
        all_movies = self.movies_df["movie_id"].unique()
        
        # Predict ratings for all movies
        predictions = []
        for movie_id in all_movies:
            pred = self.svd_model.predict(user_id, movie_id).est
            predictions.append((movie_id, pred))
        
        # Sort by predicted rating
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        # Get top N recommendations
        top_n = predictions[:n_recommendations]
        
        # Format recommendations
        recommendations = []
        for movie_id, pred_rating in top_n:
            movie = self.movies_df[self.movies_df["movie_id"] == movie_id].iloc[0]
            recommendations.append({
                "movie_id": movie_id,
                "title": movie["title"],
                "predicted_rating": round(pred_rating, 2),
                "genres": movie["genres"]
            })
        
        return recommendations
    
    def load_model(self, run_id):
        """Load model from MLflow"""
        try:
            # Load models from MLflow
            logged_model = f"runs:/{run_id}/svd_model"
            self.svd_model = mlflow.pyfunc.load_model(logged_model)
            
            logged_vectorizer = f"runs:/{run_id}/tfidf_vectorizer"
            self.tfidf_vectorizer = mlflow.sklearn.load_model(logged_vectorizer)
            
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
