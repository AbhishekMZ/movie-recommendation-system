import pandas as pd
import numpy as np
from typing import Tuple, List

class DataLoader:
    def __init__(self, ratings_path: str, movies_path: str):
        """
        Initialize the DataLoader with paths to ratings and movies datasets
        
        Args:
            ratings_path (str): Path to ratings CSV file
            movies_path (str): Path to movies CSV file
        """
        self.ratings_df = pd.read_csv(ratings_path)
        self.movies_df = pd.read_csv(movies_path)
    
    def preprocess_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Preprocess the ratings and movies data
        
        Returns:
            Tuple of preprocessed ratings and movies DataFrames
        """
        # Clean and prepare ratings data
        self.ratings_df = self.ratings_df.dropna()
        self.ratings_df['rating'] = self.ratings_df['rating'].astype(float)
        
        # Clean and prepare movies data
        self.movies_df = self.movies_df.dropna()
        
        return self.ratings_df, self.movies_df
    
    def get_user_movie_matrix(self) -> pd.DataFrame:
        """
        Create a user-movie interaction matrix
        
        Returns:
            DataFrame representing user-movie interactions
        """
        user_movie_matrix = self.ratings_df.pivot(
            index='userId', 
            columns='movieId', 
            values='rating'
        ).fillna(0)
        
        return user_movie_matrix
