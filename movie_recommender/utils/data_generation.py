import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataGenerator:
    """Class for generating synthetic data for testing and development."""
    
    def __init__(self, random_state: int = 42):
        """Initialize data generator with given random state."""
        self.random_state = random_state
        np.random.seed(random_state)
        random.seed(random_state)
        
        # Parameters for generating realistic data
        self.rating_bias = 0.2  # Standard deviation for user/item rating biases
        self.noise_level = 0.1  # Standard deviation for random noise
        self.n_genres = 5      # Number of latent genre factors
    
    def generate_user_profiles(self, n_users: int) -> Dict[str, Dict[str, float]]:
        """Generate user profiles with preferences."""
        profiles = {}
        
        for i in range(n_users):
            user_id = f'U{i+1}'
            
            # Generate user preferences
            profile = {
                'genre_preferences': np.random.normal(0, 1, self.n_genres),
                'rating_bias': np.random.normal(0, self.rating_bias),
                'activity_level': np.random.gamma(2, 2),  # Some users rate more than others
                'diversity_preference': np.random.beta(2, 5)  # Preference for diverse content
            }
            
            profiles[user_id] = profile
        
        return profiles
    
    def generate_content_features(self, n_items: int) -> Dict[str, Dict[str, Any]]:
        """Generate content features including genre factors."""
        features = {}
        
        for i in range(n_items):
            content_id = f'M{i+1}'
            
            # Generate content characteristics
            feature = {
                'genre_factors': np.random.normal(0, 1, self.n_genres),
                'quality_bias': np.random.normal(0, self.rating_bias),
                'release_year': np.random.randint(1990, 2024),
                'popularity': np.random.beta(2, 5),
                'complexity': np.random.normal(0, 1)
            }
            
            features[content_id] = feature
        
        return features
    
    def generate_ratings(self, user_profiles: Dict[str, Dict[str, float]],
                        content_features: Dict[str, Dict[str, Any]],
                        sparsity: float = 0.1) -> pd.DataFrame:
        """Generate ratings based on user profiles and content features."""
        ratings_data = []
        
        n_users = len(user_profiles)
        n_items = len(content_features)
        n_ratings = int(n_users * n_items * sparsity)
        
        # Generate user-item interactions
        for _ in range(n_ratings):
            user_id = random.choice(list(user_profiles.keys()))
            content_id = random.choice(list(content_features.keys()))
            
            # Calculate rating based on user-item interaction
            user_profile = user_profiles[user_id]
            content_feature = content_features[content_id]
            
            # Base rating from genre preferences
            base_rating = np.dot(user_profile['genre_preferences'],
                               content_feature['genre_factors'])
            
            # Add biases and noise
            rating = (3.5 +  # Base rating
                     base_rating +  # User-item interaction
                     user_profile['rating_bias'] +  # User bias
                     content_feature['quality_bias'] +  # Item bias
                     np.random.normal(0, self.noise_level))  # Random noise
            
            # Temporal effect (items get slightly lower ratings over time)
            years_old = 2024 - content_feature['release_year']
            temporal_effect = -0.1 * (years_old / 30)  # Max effect of -0.1 for very old items
            
            # Final rating
            final_rating = np.clip(rating + temporal_effect, 1, 5)
            
            # Add timestamp
            days_ago = np.random.exponential(100)  # More recent ratings are more likely
            timestamp = datetime.now() - timedelta(days=days_ago)
            
            ratings_data.append({
                'user_id': user_id,
                'content_id': content_id,
                'rating': final_rating,
                'timestamp': timestamp
            })
        
        # Convert to DataFrame and sort by timestamp
        df = pd.DataFrame(ratings_data)
        df = df.sort_values('timestamp')
        
        return df
    
    def generate_dataset(self, n_users: int = 100, n_items: int = 200,
                        sparsity: float = 0.1) -> Tuple[pd.DataFrame, Dict, Dict]:
        """Generate complete dataset including ratings, user profiles, and content features."""
        logger.info(f"Generating synthetic dataset with {n_users} users and {n_items} items...")
        
        # Generate user profiles and content features
        user_profiles = self.generate_user_profiles(n_users)
        content_features = self.generate_content_features(n_items)
        
        # Generate ratings
        ratings_df = self.generate_ratings(user_profiles, content_features, sparsity)
        
        logger.info(f"Generated {len(ratings_df)} ratings")
        logger.info(f"Average ratings per user: {len(ratings_df)/n_users:.2f}")
        logger.info(f"Rating distribution:\n{ratings_df['rating'].value_counts(normalize=True).sort_index()}")
        
        return ratings_df, user_profiles, content_features

def main():
    """Example usage of data generation."""
    try:
        # Initialize generator
        generator = DataGenerator(random_state=42)
        
        # Generate dataset
        ratings_df, user_profiles, content_features = generator.generate_dataset(
            n_users=100,
            n_items=200,
            sparsity=0.1
        )
        
        # Save generated data
        output_dir = Path(__file__).parent.parent / "data"
        output_dir.mkdir(exist_ok=True)
        
        ratings_df.to_csv(output_dir / "synthetic_ratings.csv", index=False)
        
        # Print summary statistics
        print("\nDataset Statistics:")
        print(f"Total ratings: {len(ratings_df)}")
        print(f"Unique users: {ratings_df['user_id'].nunique()}")
        print(f"Unique items: {ratings_df['content_id'].nunique()}")
        print("\nRating distribution:")
        print(ratings_df['rating'].describe())
        
    except Exception as e:
        logger.error(f"Error generating data: {str(e)}")

if __name__ == "__main__":
    main()
