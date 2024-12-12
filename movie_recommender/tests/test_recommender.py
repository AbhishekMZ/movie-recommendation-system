import unittest
import pandas as pd
import numpy as np
from core.hybrid_recommender import HybridRecommender

class TestRecommender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Create sample content data
        cls.content_data = pd.DataFrame({
            'content_id': ['C1', 'C2', 'C3'],
            'title': ['Movie 1', 'Movie 2', 'Movie 3'],
            'description': ['Action movie', 'Comedy movie', 'Drama movie'],
            'genres': ['Action', 'Comedy', 'Drama']
        })
        
        # Create sample viewing history
        cls.viewing_history = pd.DataFrame({
            'user_id': ['U1', 'U1', 'U2'],
            'content_id': ['C1', 'C2', 'C3'],
            'watch_duration': [100, 200, 150],
            'timestamp': pd.date_range(start='2024-01-01', periods=3)
        })
        
        # Save test data
        cls.content_data.to_csv('test_content.csv', index=False)
        cls.viewing_history.to_csv('test_viewing.csv', index=False)
        
        # Initialize recommender
        cls.recommender = HybridRecommender('test_content.csv', 'test_viewing.csv')
        cls.recommender.train(n_components=2)

    def test_content_based_recommendations(self):
        """Test content-based recommendations"""
        recs = self.recommender.get_content_based_recommendations('C1', n_recommendations=2)
        self.assertEqual(len(recs), 2)
        self.assertTrue(all(isinstance(score, float) for _, score in recs))

    def test_collaborative_recommendations(self):
        """Test collaborative filtering recommendations"""
        recs = self.recommender.get_collaborative_recommendations('U1', n_recommendations=2)
        self.assertEqual(len(recs), 2)
        self.assertTrue(all(isinstance(score, float) for _, score in recs))

    def test_hybrid_recommendations(self):
        """Test hybrid recommendations"""
        recs = self.recommender.get_hybrid_recommendations('U1', n_recommendations=2)
        self.assertEqual(len(recs), 2)
        self.assertTrue(all(isinstance(r['predicted_rating'], float) for r in recs))
        self.assertTrue(all(0 <= r['predicted_rating'] <= 5 for r in recs))

if __name__ == '__main__':
    unittest.main()
