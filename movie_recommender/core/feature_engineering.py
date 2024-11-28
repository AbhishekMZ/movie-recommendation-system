import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieFeatureEngineer:
    def __init__(self):
        """Initialize feature engineering components."""
        self.scaler = StandardScaler()
        self.genre_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        self.tfidf = TfidfVectorizer(max_features=100, stop_words='english')
        
    def extract_content_features(self, content_df):
        """Extract content-based features from movie metadata.
        
        Key Features:
        1. Basic Metadata:
           - Duration (normalized)
           - Release Year (normalized)
           - Content Rating
           
        2. Genre Features:
           - One-hot encoded genres
           - Genre popularity scores
           
        3. Text-based Features:
           - TF-IDF vectors from description
           - TF-IDF vectors from title
           
        4. Cast and Crew:
           - Director encoding
           - Top cast members encoding
           - Director's average rating
           - Cast members' average rating
        """
        features = {}
        
        # 1. Basic Metadata Features
        features['duration'] = self._process_duration(content_df['duration'])
        features['release_year'] = self._normalize_years(content_df['release_year'])
        features['content_rating'] = self._encode_ratings(content_df['rating'])
        
        # 2. Genre Features
        genre_features = self._process_genres(content_df['listed_in'])
        features.update(genre_features)
        
        # 3. Text Features
        text_features = self._process_text_features(
            content_df['description'],
            content_df['title']
        )
        features.update(text_features)
        
        # 4. Cast and Crew Features
        cast_features = self._process_cast_crew(
            content_df['director'],
            content_df['cast']
        )
        features.update(cast_features)
        
        return pd.DataFrame(features)
    
    def extract_user_features(self, viewing_history_df, content_df):
        """Extract user behavior and preference features.
        
        Key Features:
        1. Viewing Patterns:
           - Average watch duration
           - Preferred viewing times
           - Binge-watching tendency
           
        2. Genre Preferences:
           - Genre watch counts
           - Genre completion rates
           - Genre average ratings
           
        3. Rating Behavior:
           - Average rating given
           - Rating variance
           - Rating count
           
        4. Content Type Preferences:
           - Movie vs. TV show preference
           - Preferred content duration
           - Preferred release years
        """
        features = {}
        
        # 1. Viewing Pattern Features
        viewing_patterns = self._analyze_viewing_patterns(viewing_history_df)
        features.update(viewing_patterns)
        
        # 2. Genre Preference Features
        genre_prefs = self._analyze_genre_preferences(
            viewing_history_df,
            content_df
        )
        features.update(genre_prefs)
        
        # 3. Rating Behavior Features
        rating_features = self._analyze_rating_behavior(viewing_history_df)
        features.update(rating_features)
        
        # 4. Content Type Preference Features
        content_prefs = self._analyze_content_preferences(
            viewing_history_df,
            content_df
        )
        features.update(content_prefs)
        
        return pd.DataFrame(features)
    
    def extract_interaction_features(self, user_id, content_id, viewing_history_df, content_df):
        """Extract user-content interaction features.
        
        Key Features:
        1. Historical Interactions:
           - Previous views count
           - Average completion rate
           - Last rating given
           
        2. Content Similarity:
           - Genre similarity to watched content
           - Cast/crew overlap with watched content
           - Text similarity to watched content
           
        3. Temporal Features:
           - Time since last view
           - Viewing time patterns
           - Seasonal preferences
           
        4. Social Features:
           - Similar users' ratings
           - Similar users' completion rates
           - Content popularity among similar users
        """
        features = {}
        
        # 1. Historical Interaction Features
        history_features = self._analyze_historical_interactions(
            user_id, content_id, viewing_history_df
        )
        features.update(history_features)
        
        # 2. Content Similarity Features
        similarity_features = self._calculate_content_similarity(
            user_id, content_id, viewing_history_df, content_df
        )
        features.update(similarity_features)
        
        # 3. Temporal Features
        temporal_features = self._extract_temporal_features(
            user_id, content_id, viewing_history_df
        )
        features.update(temporal_features)
        
        # 4. Social Features
        social_features = self._calculate_social_features(
            user_id, content_id, viewing_history_df
        )
        features.update(social_features)
        
        return pd.Series(features)
    
    def _process_duration(self, duration_series):
        """Convert duration strings to minutes and normalize."""
        # Extract numeric duration
        duration_min = pd.to_numeric(
            duration_series.str.extract('(\d+)')[0],
            errors='coerce'
        )
        
        # Handle TV shows (assume average 45 min per episode, 10 episodes per season)
        mask = duration_series.str.contains('Season', na=False)
        duration_min.loc[mask] = duration_min.loc[mask] * 10 * 45
        
        # Normalize
        return self.scaler.fit_transform(duration_min.values.reshape(-1, 1)).ravel()
    
    def _normalize_years(self, year_series):
        """Normalize release years."""
        return self.scaler.fit_transform(year_series.values.reshape(-1, 1)).ravel()
    
    def _encode_ratings(self, rating_series):
        """Encode content ratings into numerical values."""
        rating_map = {
            'G': 1, 'TV-Y': 1,
            'PG': 2, 'TV-Y7': 2,
            'PG-13': 3, 'TV-PG': 3,
            'R': 4, 'TV-14': 4,
            'NC-17': 5, 'TV-MA': 5
        }
        return rating_series.map(rating_map).fillna(3)
    
    def _process_genres(self, genre_series):
        """Process and encode genres."""
        # Split genres and one-hot encode
        genres = genre_series.str.get_dummies(sep=', ')
        return {f'genre_{col}': genres[col] for col in genres.columns}
    
    def _process_text_features(self, descriptions, titles):
        """Extract features from text fields."""
        # Process descriptions
        desc_vectors = self.tfidf.fit_transform(descriptions.fillna(''))
        desc_features = {
            f'desc_key_{i}': desc_vectors[:, i].toarray().ravel()
            for i in range(desc_vectors.shape[1])
        }
        
        # Process titles
        title_vectors = self.tfidf.fit_transform(titles)
        title_features = {
            f'title_key_{i}': title_vectors[:, i].toarray().ravel()
            for i in range(title_vectors.shape[1])
        }
        
        return {**desc_features, **title_features}
    
    def _process_cast_crew(self, directors, cast):
        """Process cast and crew information."""
        # Encode directors
        director_features = pd.get_dummies(
            directors.fillna('unknown'),
            prefix='director'
        )
        
        # Process cast (take top 3 cast members)
        cast = cast.fillna('').str.split(',').str[:3]
        cast_features = pd.get_dummies(
            pd.DataFrame(cast.tolist()).fillna('unknown'),
            prefix='cast'
        )
        
        features = {}
        features.update({
            f'director_{col}': director_features[col]
            for col in director_features.columns
        })
        features.update({
            f'cast_{col}': cast_features[col]
            for col in cast_features.columns
        })
        
        return features

def main():
    """Example usage of feature engineering."""
    try:
        # Load data
        viewing_history = pd.read_csv('data/combined/viewing_history.csv')
        content_data = pd.read_csv('data/combined/streaming_combined.csv')
        
        # Initialize feature engineer
        engineer = MovieFeatureEngineer()
        
        # Extract content features
        content_features = engineer.extract_content_features(content_data)
        logger.info(f"Generated {len(content_features.columns)} content features")
        
        # Extract user features
        user_features = engineer.extract_user_features(viewing_history, content_data)
        logger.info(f"Generated {len(user_features.columns)} user features")
        
        # Example: Extract interaction features for a specific user-content pair
        if len(viewing_history) > 0 and len(content_data) > 0:
            sample_user_id = viewing_history['user_id'].iloc[0]
            sample_content_id = content_data['content_id'].iloc[0]
            
            interaction_features = engineer.extract_interaction_features(
                sample_user_id, sample_content_id,
                viewing_history, content_data
            )
            logger.info(f"Generated {len(interaction_features)} interaction features")
        
    except Exception as e:
        logger.error(f"Error in feature engineering: {str(e)}")

if __name__ == "__main__":
    main()
