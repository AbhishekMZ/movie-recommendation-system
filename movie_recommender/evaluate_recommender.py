import pandas as pd
import numpy as np
from core.streaming_recommender import StreamingRecommender
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, ndcg_score
import logging
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommenderEvaluator:
    def __init__(self, recommender, test_history, k_values=[5, 10, 20]):
        self.recommender = recommender
        self.test_history = test_history
        self.k_values = k_values

    def evaluate(self):
        metrics = {}
        
        # Get test users
        test_users = self.test_history['user_id'].unique()
        
        # Evaluate rating prediction accuracy
        rmse, mae, r2 = self.recommender.evaluate_prediction_accuracy(test_users)
        metrics['RMSE'] = rmse
        metrics['MAE'] = mae
        metrics['R_squared'] = r2
        
        # Generate predictions for all users in test set
        predictions = {}
        for user_id in test_users:
            try:
                user_recs_df = self.recommender.get_user_recommendations(user_id, max(self.k_values))
                predictions[user_id] = dict(zip(user_recs_df['content_id'], user_recs_df['score']))
                
                # Get expected ratings for logging
                expected = self.recommender.calculate_expected_ratings(user_id, user_recs_df['content_id'].tolist())
                logger.info(f"\nUser {user_id} Recommendations:")
                for cid in user_recs_df['content_id'][:5]:  # Show top 5
                    pred_rating = self.recommender.predict_user_rating(user_id, cid)
                    exp_rating = expected.get(cid, 'N/A')
                    logger.info(f"Content {cid}: Predicted={pred_rating:.2f}, Expected={exp_rating}")
            except KeyError:
                continue
        
        # Calculate ranking metrics for different k values
        for k in self.k_values:
            logger.info(f"\nCalculating metrics for k={k}")
            
            # Calculate Hit Rate@k
            hit_rate = self._calculate_hit_rate(predictions, k)
            metrics[f'Hit Rate@{k}'] = hit_rate
            logger.info(f"Hit Rate@{k}: {hit_rate:.3f}")
            
            # Calculate NDCG@k
            ndcg = self._calculate_ndcg(predictions, k)
            metrics[f'NDCG@{k}'] = ndcg
            logger.info(f"NDCG@{k}: {ndcg:.3f}")
        
        return metrics

    def _calculate_hit_rate(self, predictions, k):
        """Calculate Hit Rate@k"""
        hits = 0
        total = 0
        
        for user_id, user_preds in tqdm(predictions.items(), desc="Calculating Hit Rate"):
            # Get top k predictions
            top_k = sorted(user_preds.items(), key=lambda x: x[1], reverse=True)[:k]
            top_k_items = {item[0] for item in top_k}
            
            # Get actual items from test set
            actual_items = set(self.test_history[self.test_history['user_id'] == user_id]['content_id'])
            
            # Calculate hit
            if len(actual_items.intersection(top_k_items)) > 0:
                hits += 1
            total += 1
        
        return hits / total if total > 0 else 0

    def _calculate_ndcg(self, predictions, k):
        """Calculate NDCG@k"""
        ndcg_scores = []
        
        for user_id, user_preds in tqdm(predictions.items(), desc="Calculating NDCG"):
            # Get top k predictions
            top_k = sorted(user_preds.items(), key=lambda x: x[1], reverse=True)[:k]
            pred_items = [item[0] for item in top_k]
            
            # Create relevance array (1 if item in test set, 0 otherwise)
            actual_items = set(self.test_history[self.test_history['user_id'] == user_id]['content_id'])
            rel = [1 if item in actual_items else 0 for item in pred_items]
            
            # Calculate DCG
            dcg = sum((2**r - 1) / np.log2(i + 2) for i, r in enumerate(rel))
            
            # Calculate IDCG
            ideal_rel = sorted(rel, reverse=True)
            idcg = sum((2**r - 1) / np.log2(i + 2) for i, r in enumerate(ideal_rel))
            
            # Calculate NDCG
            ndcg = dcg / idcg if idcg > 0 else 0
            ndcg_scores.append(ndcg)
        
        return np.mean(ndcg_scores)

def main():
    try:
        # Set up paths
        project_root = Path(__file__).parent.parent
        content_path = project_root / 'data' / 'combined' / 'streaming_combined.csv'
        history_path = project_root / 'data' / 'combined' / 'viewing_history.csv'
        output_dir = project_root / 'evaluations'
        
        # Initialize recommender
        recommender = StreamingRecommender(n_components=50)
        
        # Prepare data
        history_df = pd.read_csv(history_path)
        train_history, test_history = train_test_split(history_df, test_size=0.2, random_state=42)
        
        # Train recommender
        recommender.load_data(content_path, train_history)
        recommender.fit()
        
        # Initialize and run evaluator
        evaluator = RecommenderEvaluator(recommender, test_history)
        metrics = evaluator.evaluate()
        
        # Save metrics to file
        metrics_df = pd.DataFrame([metrics])
        metrics_df.to_csv(output_dir / 'evaluation_metrics.csv', index=False)
        
        logger.info(f"\nEvaluation results saved to {output_dir}")
        
    except Exception as e:
        logger.error(f"Error in evaluation: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
