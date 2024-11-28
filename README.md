# Movie Recommendation System

This is a machine learning-powered movie recommendation system that provides personalized movie suggestions based on user preferences and collaborative filtering.

## Features

- Personalized movie recommendations using SVD (Singular Value Decomposition)
- Handles cold-start problem with popularity-based recommendations
- RESTful API endpoints for easy integration
- Model persistence for quick loading
- Scalable architecture

## Setup

1. Create a `.env` file in the root directory with the following content:
```
DATA_DIR=data
```

2. Place your movie dataset files in the `data` directory:
   - `movies.csv`: Contains movie information (movieId, title, etc.)
   - `ratings.csv`: Contains user ratings (userId, movieId, rating, timestamp)

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the Flask server:
```bash
python movie_recommender/app.py
```

## API Endpoints

### Get Recommendations

```
GET /recommend?user_id=<user_id>&n=<number_of_recommendations>
```

Parameters:
- `user_id`: ID of the user to get recommendations for
- `n` (optional): Number of recommendations to return (default: 10)

### Get Popular Movies

```
GET /popular?n=<number_of_movies>
```

Parameters:
- `n` (optional): Number of popular movies to return (default: 10)

## Project Objectives

### Primary Objectives
1. **Personalized Content Discovery**
   - Provide tailored movie and TV show recommendations based on user viewing history
   - Adapt to changing user preferences over time
   - Handle both explicit (ratings) and implicit (viewing completion) feedback

2. **Cross-Platform Integration**
   - Seamlessly combine content from Netflix, Amazon Prime, and Disney+
   - Normalize content metadata across platforms
   - Maintain platform-specific content identifiers

3. **Performance Metrics**
   - Achieve high recommendation accuracy (target: >80% precision@10)
   - Minimize recommendation latency (<100ms per request)
   - Maintain diversity in recommendations

4. **User Experience**
   - Cold-start handling for new users
   - Real-time recommendation updates
   - Transparent recommendation reasoning

### Technical Objectives
1. **Algorithm Implementation**
   - Develop hybrid recommendation system combining:
     * Collaborative filtering (user-user and item-item)
     * Content-based filtering
     * Popularity-based recommendations
   - Implement efficient matrix factorization techniques
   - Utilize deep learning for feature extraction

2. **System Architecture**
   - Build scalable recommendation pipeline
   - Implement efficient data preprocessing
   - Design modular and maintainable codebase
   - Enable easy integration of new data sources

3. **Data Management**
   - Handle large-scale user interaction data
   - Implement efficient data update mechanisms
   - Ensure data quality and consistency
   - Support incremental model updates

4. **Evaluation Framework**
   - Implement comprehensive testing suite
   - Set up A/B testing infrastructure
   - Monitor recommendation quality metrics
   - Track user engagement metrics

### Business Objectives
1. **User Engagement**
   - Increase average viewing time
   - Improve content discovery
   - Reduce browsing time before playback
   - Increase user retention

2. **Content Utilization**
   - Improve long-tail content discovery
   - Balance popular and niche content recommendations
   - Optimize content licensing ROI
   - Support content acquisition decisions

3. **Platform Growth**
   - Support user base scaling
   - Enable new feature integration
   - Facilitate cross-platform content discovery
   - Support international audience

4. **Quality Assurance**
   - Ensure recommendation relevance
   - Maintain system reliability
   - Support content moderation
   - Enable easy debugging and monitoring

## Implementation Details

The recommendation system uses a hybrid approach:

1. For existing users:
   - Collaborative filtering using SVD algorithm
   - Predicts ratings for unwatched movies
   - Returns top-N movies with highest predicted ratings

2. For new users (cold-start):
   - Returns popular movies based on average rating and number of ratings
   - Uses a weighted score that considers both rating average and popularity

## Data Format

### movies.csv
```
movieId,title,genres
1,Toy Story (1995),Adventure|Animation|Children|Comedy|Fantasy
```

### ratings.csv
```
userId,movieId,rating,timestamp
1,1,4.0,964982703
```
