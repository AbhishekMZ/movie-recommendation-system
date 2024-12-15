# API Documentation

## Base URL
```
Development: http://localhost:8000
Production: https://api.movierecommender.com
```

## Authentication

### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "token": "string"
}
```

### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "token": "string",
  "token_type": "bearer"
}
```

## Recommendations

### Get Personalized Recommendations
```http
GET /recommendations
```

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `limit` (optional): Number of recommendations (default: 10)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "recommendations": [
    {
      "movie_id": "string",
      "title": "string",
      "genres": ["string"],
      "predicted_rating": number,
      "confidence_score": number
    }
  ],
  "total": number,
  "offset": number,
  "limit": number
}
```

### Submit Rating
```http
POST /ratings
```

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "movie_id": "string",
  "rating": number,
  "timestamp": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Rating submitted successfully"
}
```

### Get Popular Movies
```http
GET /movies/popular
```

**Query Parameters:**
- `limit` (optional): Number of movies (default: 10)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "movies": [
    {
      "id": "string",
      "title": "string",
      "genres": ["string"],
      "average_rating": number,
      "rating_count": number
    }
  ],
  "total": number,
  "offset": number,
  "limit": number
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid input parameters",
  "details": {}
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting
- Rate limit: 100 requests per minute
- Headers included in response:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Versioning
API versioning is handled through the URL:
- Current version: `/v1/`
- Legacy support: Available for previous versions
- Deprecation notice: Provided 6 months in advance
