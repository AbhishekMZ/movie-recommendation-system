import pandas as pd
from core.streaming_recommender import StreamingRecommender
import logging
from pathlib import Path
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_all_user_recommendations(recommender, n_recommendations=3):
    """Generate recommendations for all users.
    
    Args:
        recommender: Trained StreamingRecommender instance
        n_recommendations: Number of recommendations per user
        
    Returns:
        DataFrame with recommendations for all users
    """
    all_recommendations = []
    
    # Get all users
    users = recommender.viewing_history['user_id'].unique()
    
    # Generate recommendations for each user with progress bar
    logger.info(f"Generating recommendations for {len(users)} users...")
    for user_id in tqdm(users, desc="Generating recommendations"):
        # Get recommendations for user
        user_recs = recommender.get_user_recommendations(user_id, n_recommendations)
        
        # Add user_id to recommendations
        user_recs['user_id'] = user_id
        user_recs['rank'] = range(1, len(user_recs) + 1)
        
        all_recommendations.append(user_recs)
    
    # Combine all recommendations
    recommendations_df = pd.concat(all_recommendations, ignore_index=True)
    
    # Reorder columns for better readability
    columns_order = ['user_id', 'rank', 'title', 'type', 'source', 'score', 'content_id']
    recommendations_df = recommendations_df[columns_order]
    
    return recommendations_df

def main():
    try:
        # Initialize recommender
        recommender = StreamingRecommender(n_components=50)
        
        # Get correct paths
        project_root = Path(__file__).parent.parent
        content_path = project_root / 'data' / 'combined' / 'streaming_combined.csv'
        history_path = project_root / 'data' / 'combined' / 'viewing_history.csv'
        
        logger.info(f"Loading data from:\n{content_path}\n{history_path}")
        
        # Load and train model
        recommender.load_data(str(content_path), str(history_path))
        recommender.fit()
        
        # Generate recommendations for all users
        recommendations_df = generate_all_user_recommendations(recommender, n_recommendations=3)
        
        # Save recommendations to CSV
        output_path = project_root / 'data' / 'recommendations' / 'user_recommendations.csv'
        output_path.parent.mkdir(exist_ok=True)
        recommendations_df.to_csv(output_path, index=False)
        
        # Print sample and statistics
        logger.info("\nSample of recommendations:")
        print(recommendations_df.head(9))  # Show first 3 recommendations for 3 users
        
        logger.info(f"\nRecommendations statistics:")
        logger.info(f"Total recommendations: {len(recommendations_df)}")
        logger.info(f"Users with recommendations: {recommendations_df['user_id'].nunique()}")
        logger.info(f"Average recommendation score: {recommendations_df['score'].mean():.3f}")
        
        # Show distribution of recommendations by source
        logger.info("\nRecommendations by source:")
        source_dist = recommendations_df['source'].value_counts()
        print(source_dist)
        
        logger.info(f"\nRecommendations saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")

if __name__ == "__main__":
    main()
