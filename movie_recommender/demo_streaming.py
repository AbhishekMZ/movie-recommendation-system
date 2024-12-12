import os
from core.streaming_recommender import StreamingRecommender
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Demo the streaming recommendation system."""
    try:
        # Initialize recommender
        recommender = StreamingRecommender(n_components=50)
        
        # Get correct paths
        project_root = Path(__file__).parent.parent
        content_path = project_root / 'data' / 'combined' / 'streaming_combined.csv'
        history_path = project_root / 'data' / 'combined' / 'viewing_history.csv'
        
        logger.info(f"Loading data from:\n{content_path}\n{history_path}")
        
        recommender.load_data(str(content_path), str(history_path))
        
        # Train the model
        recommender.fit()
        
        # Demo different recommendation types
        
        # 1. Get popular recommendations
        logger.info("\nPopular Content Recommendations:")
        popular_content = recommender.get_popular_recommendations(n_recommendations=5)
        print(popular_content)
        
        # 2. Get personalized recommendations for a sample user
        sample_user = recommender.viewing_history['user_id'].iloc[0]
        logger.info(f"\nPersonalized Recommendations for User {sample_user}:")
        user_recommendations = recommender.get_user_recommendations(sample_user, n_recommendations=5)
        print(user_recommendations)
        
        # 3. Get similar content recommendations
        sample_content = recommender.content_data['content_id'].iloc[0]
        logger.info(f"\nSimilar Content Recommendations for {sample_content}:")
        similar_content = recommender.get_similar_content(sample_content, n_recommendations=5)
        print(similar_content)
        
    except Exception as e:
        logger.error(f"Error in demo: {str(e)}")

if __name__ == "__main__":
    main()
