import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeyFeatureVisualizer:
    def __init__(self):
        self.output_dir = Path('visualizations')
        self.output_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        self.colors = sns.color_palette("husl", 8)
    
    def plot_genre_correlation(self, content_df, viewing_history_df):
        """Plot correlation heatmap between genres."""
        # Merge data
        merged_data = pd.merge(
            viewing_history_df,
            content_df[['content_id', 'listed_in']],
            on='content_id'
        )
        
        # Split genres and create a binary matrix
        merged_data['genre'] = merged_data['listed_in'].str.split(', ')
        genres_exploded = merged_data.explode('genre')
        
        # Create user-genre matrix
        user_genre_matrix = pd.crosstab(
            genres_exploded['user_id'],
            genres_exploded['genre']
        )
        
        # Calculate genre correlations
        genre_correlations = user_genre_matrix.corr()
        
        # Keep top 15 genres by frequency for better visualization
        top_genres = user_genre_matrix.sum().sort_values(ascending=False).head(15).index
        genre_correlations = genre_correlations.loc[top_genres, top_genres]
        
        # Create heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(genre_correlations, 
                   annot=True,
                   cmap='RdYlBu',
                   center=0,
                   fmt='.2f',
                   square=True)
        
        plt.title('Genre Correlation Heatmap\n(Based on User Viewing Patterns)')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'genre_correlation.png')
        plt.close()
        
        return genre_correlations

    def plot_genre_popularity(self, content_df, viewing_history_df):
        """Plot most popular genres by watch count."""
        # Merge data
        merged_data = pd.merge(
            viewing_history_df,
            content_df[['content_id', 'listed_in']],
            on='content_id'
        )
        
        # Split genres and explode to get one genre per row
        merged_data['genre'] = merged_data['listed_in'].str.split(', ')
        genre_data = merged_data.explode('genre')
        
        # Calculate genre metrics
        genre_stats = genre_data.groupby('genre').agg({
            'user_id': 'count'  # Number of views
        }).reset_index()
        
        genre_stats.columns = ['genre', 'view_count']
        genre_stats = genre_stats.sort_values('view_count', ascending=False).head(10)
        
        # Create plot
        plt.figure(figsize=(12, 6))
        
        # Plot view counts
        plt.barh(genre_stats['genre'], genre_stats['view_count'],
                color=self.colors[0], alpha=0.6)
        
        plt.title('Most Popular Genres by View Count')
        plt.xlabel('Number of Views')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'genre_popularity.png')
        plt.close()
        
        return genre_stats
    
    def plot_rating_distribution(self, viewing_history_df):
        """Plot distribution of user ratings."""
        plt.figure(figsize=(10, 6))
        
        # Create histogram of ratings
        sns.histplot(data=viewing_history_df, x='rating',
                    bins=10, color=self.colors[1])
        
        plt.title('Distribution of User Ratings')
        plt.xlabel('Rating')
        plt.ylabel('Count')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'rating_distribution.png')
        plt.close()

def main():
    """Generate visualizations for key features."""
    try:
        # Load data
        viewing_history = pd.read_csv('data/combined/viewing_history.csv')
        content_data = pd.read_csv('data/combined/streaming_combined.csv')
        
        # Rename columns for consistency
        content_data = content_data.rename(columns={'unique_id': 'content_id'})
        
        # Initialize visualizer
        visualizer = KeyFeatureVisualizer()
        
        # 1. Genre Correlation
        genre_corr = visualizer.plot_genre_correlation(content_data, viewing_history)
        logger.info("\nGenre Correlation Matrix:")
        print("\nTop Genre Correlations:")
        # Print top 5 most correlated genre pairs
        corr_pairs = []
        for i in range(len(genre_corr.columns)):
            for j in range(i+1, len(genre_corr.columns)):
                corr_pairs.append((
                    genre_corr.index[i],
                    genre_corr.columns[j],
                    genre_corr.iloc[i, j]
                ))
        top_correlations = sorted(corr_pairs, key=lambda x: abs(x[2]), reverse=True)[:5]
        for g1, g2, corr in top_correlations:
            print(f"{g1} - {g2}: {corr:.3f}")
        
        # 2. Genre Popularity
        genre_stats = visualizer.plot_genre_popularity(content_data, viewing_history)
        logger.info("\nTop Genres by Popularity:")
        print(genre_stats)
        
        # 3. Rating Distribution
        visualizer.plot_rating_distribution(viewing_history)
        logger.info("\nRating Statistics:")
        print(viewing_history['rating'].describe())
        
        logger.info("\nSuccessfully generated all visualizations")
        
    except Exception as e:
        logger.error(f"Error generating visualizations: {str(e)}")

if __name__ == "__main__":
    main()
