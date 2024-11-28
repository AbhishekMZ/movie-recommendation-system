from flask import Flask, request, jsonify
from recommender import MovieRecommender
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
recommender = MovieRecommender()

# Initialize the recommender with data
@app.before_first_request
def initialize():
    data_dir = os.getenv('DATA_DIR', 'data')
    movies_path = os.path.join(data_dir, 'movies.csv')
    ratings_path = os.path.join(data_dir, 'ratings.csv')
    
    recommender.load_data(movies_path, ratings_path)
    recommender.preprocess_data()
    
    # Try to load existing model, train new one if not found
    model_path = os.path.join(data_dir, 'model.pkl')
    if os.path.exists(model_path):
        recommender.load_model(model_path)
    else:
        recommender.train_model()
        recommender.save_model(model_path)

@app.route('/recommend', methods=['GET'])
def get_recommendations():
    try:
        user_id = int(request.args.get('user_id'))
        n_recommendations = int(request.args.get('n', 10))
        
        recommendations = recommender.get_user_recommendations(
            user_id, 
            n_recommendations
        )
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/popular', methods=['GET'])
def get_popular():
    try:
        n_recommendations = int(request.args.get('n', 10))
        popular_movies = recommender._get_popular_movies(n_recommendations)
        
        return jsonify({
            'status': 'success',
            'popular_movies': popular_movies
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)
