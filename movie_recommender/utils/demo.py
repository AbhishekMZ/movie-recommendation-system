import pandas as pd
import numpy as np
from pathlib import Path
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any
from sklearn.model_selection import KFold

from ..core.svd_recommender import SVDRecommender
from ..evaluation.evaluator import ModelEvaluator
from .data_generation import DataGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecommenderDemo:
    """Class for demonstrating and analyzing recommender system performance."""
    
    def __init__(self, results_dir: str = None):
        """Initialize demo with optional results directory."""
        self.results_dir = Path(results_dir) if results_dir else Path(__file__).parent.parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        self.evaluator = ModelEvaluator()
        self.data_generator = DataGenerator()
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        self.colors = sns.color_palette("husl", 8)
    
    def plot_analysis_results(self, analysis_results: Dict[str, Any]):
        """Create and save visualization plots."""
        # Rating distribution plot
        plt.figure(figsize=(10, 6))
        analysis_results['rating_dist'].plot(kind='bar', alpha=0.5, label='Actual')
        plt.title('Rating Distribution')
        plt.xlabel('Rating')
        plt.ylabel('Count')
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.results_dir / 'rating_distribution.png')
        plt.close()
        
        # Error analysis plot
        plt.figure(figsize=(10, 6))
        analysis_results['error_by_rating']['mean'].plot(kind='bar')
        plt.title('Mean Prediction Error by Rating Value')
        plt.xlabel('Actual Rating')
        plt.ylabel('Mean Error')
        plt.tight_layout()
        plt.savefig(self.results_dir / 'error_analysis.png')
        plt.close()
        
        # User activity plot
        plt.figure(figsize=(10, 6))
        analysis_results['user_activity'].plot(kind='hist', bins=30)
        plt.title('User Activity Distribution')
        plt.xlabel('Number of Ratings')
        plt.ylabel('Number of Users')
        plt.tight_layout()
        plt.savefig(self.results_dir / 'user_activity.png')
        plt.close()
    
    def save_detailed_results(self, cv_results: pd.DataFrame, analysis_results: Dict[str, Any]):
        """Save detailed analysis results to file."""
        with open(self.results_dir / "detailed_analysis.txt", "w") as f:
            f.write("SVD Recommender System Analysis\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("1. Cross-Validation Results\n")
            f.write("-" * 30 + "\n")
            f.write(cv_results.to_string())
            f.write("\n\nMean Metrics:\n")
            f.write(cv_results.mean().to_string())
            f.write("\n\n")
            
            f.write("2. Rating Distribution\n")
            f.write("-" * 30 + "\n")
            f.write(analysis_results['rating_dist'].to_string())
            f.write("\n\n")
            
            f.write("3. User Statistics\n")
            f.write("-" * 30 + "\n")
            f.write("Total Users: {}\n".format(analysis_results['user_stats']['total_users']))
            f.write("Average Ratings per User: {:.2f}\n".format(
                analysis_results['user_stats']['avg_ratings_per_user']))
            f.write("90th Percentile Active Users: {:.2f}\n".format(
                analysis_results['user_stats']['active_users']))
            
            f.write("\n4. Content Statistics\n")
            f.write("-" * 30 + "\n")
            f.write("Total Items: {}\n".format(analysis_results['content_stats']['total_items']))
            f.write("Average Ratings per Item: {:.2f}\n".format(
                analysis_results['content_stats']['avg_ratings_per_item']))
    
    def run_demo(self):
        """Run complete demonstration of recommender system."""
        try:
            # Generate synthetic data
            logger.info("Generating synthetic data...")
            ratings_df, _, _ = self.data_generator.generate_dataset()
            
            # Initialize model
            logger.info("Initializing SVD recommender...")
            model = SVDRecommender(n_components=50)
            
            # Perform cross-validation
            logger.info("Performing cross-validation...")
            cv_metrics = self.evaluator.cross_validate(model, ratings_df)
            cv_results = pd.DataFrame(cv_metrics)
            
            # Train final model on full dataset
            logger.info("Training final model...")
            model.fit(ratings_df)
            
            # Analyze rating patterns
            logger.info("Analyzing rating patterns...")
            analysis_results = self.evaluator.analyze_rating_patterns(ratings_df)
            
            # Create visualizations
            logger.info("Creating visualization plots...")
            self.plot_analysis_results(analysis_results)
            
            # Save detailed results
            logger.info("Saving detailed results...")
            self.save_detailed_results(cv_results, analysis_results)
            
            # Generate sample recommendations
            logger.info("\nGenerating sample recommendations...")
            sample_users = ratings_df['user_id'].unique()[:3]
            for user_id in sample_users:
                recommendations = model.recommend_for_user(user_id, n_recommendations=5)
                logger.info(f"\nTop 5 recommendations for user {user_id}:")
                for _, row in recommendations.iterrows():
                    logger.info(f"- Movie {row['content_id']}: Predicted Rating = {row['predicted_rating']:.2f}")
            
            logger.info(f"\nDemonstration complete! Results saved to {self.results_dir}")
            
        except Exception as e:
            logger.error(f"Error in demonstration: {str(e)}")

def main():
    """Run the recommendation system demonstration."""
    demo = RecommenderDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
