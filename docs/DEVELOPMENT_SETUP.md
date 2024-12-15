# Development Setup Guide

## Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker and Docker Compose
- Kubernetes (for production deployment)

## Local Development Setup

### 1. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configurations

# Initialize database
python -m movie_recommender.scripts.init_db

# Start the backend server
uvicorn movie_recommender.api.main:app --reload
```

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 3. Database Setup
```bash
# Create database
createdb movie_recommender

# Run migrations
alembic upgrade head
```

## Running Tests
```bash
# Backend tests
pytest

# Frontend tests
cd frontend && npm test
```

## Development Workflow

### 1. Starting Development
```bash
# Start backend
uvicorn movie_recommender.api.main:app --reload

# Start frontend (in another terminal)
cd frontend && npm start

# Start database (if not running)
docker-compose up db
```

### 2. Making Changes
1. Create a new branch
2. Make changes
3. Run tests
4. Submit PR

### 3. Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Common Issues and Solutions

### Database Connection
- Ensure PostgreSQL is running
- Check connection string in .env
- Verify database exists

### Frontend Development
- Clear npm cache if dependencies fail
- Check for Node.js version compatibility
- Verify API endpoint configuration

### Backend Development
- Activate virtual environment
- Update dependencies after pulling
- Check log files for errors

## Performance Optimization Tips

### Backend
- Use async/await for I/O operations
- Implement caching for frequent queries
- Optimize database queries

### Frontend
- Implement lazy loading
- Use React.memo for expensive components
- Optimize bundle size

## Security Best Practices

### API Security
- Use JWT for authentication
- Implement rate limiting
- Validate all inputs

### Database Security
- Use parameterized queries
- Encrypt sensitive data
- Regular security audits

### Frontend Security
- Sanitize user inputs
- Implement CSP
- Use HTTPS only
