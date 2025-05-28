# Social Media Backend API

A Flask-based REST API for a social media application with user authentication, posts, and interactions.

## Features

- **User Authentication**: Registration, login with JWT tokens
- **User Profiles**: Create and update user profiles with bio, profile picture
- **Posts**: Create, read posts with timestamp and author information
- **Interactions**: Like/unlike posts
- **Database**: SQLite database with SQLAlchemy ORM
- **CORS**: Cross-origin resource sharing enabled for frontend integration

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get current user profile (requires auth)
- `PUT /api/auth/profile` - Update user profile (requires auth)

### Posts
- `GET /api/posts` - Get all posts (requires auth)
- `POST /api/posts` - Create new post (requires auth)
- `POST /api/posts/<post_id>/like` - Toggle like on post (requires auth)

### Users
- `GET /api/users/<username>` - Get user by username (requires auth)

### Health
- `GET /api/health` - Health check endpoint

## Setup and Installation

1. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**:
   - Copy `.env.example` to `.env`
   - Update configuration values as needed

4. **Run the Application**:
   ```bash
   ./run.sh
   # or
   source venv/bin/activate && python app.py
   ```

The server will start on `http://localhost:5000`

## Database Models

### User
- `id`: Unique identifier (UUID)
- `username`: Unique username
- `email`: User email address
- `password_hash`: Hashed password
- `display_name`: Display name for the user
- `bio`: User biography
- `profile_picture`: Profile picture URL
- `followers_count`: Number of followers
- `following_count`: Number of users following
- `created_at`: Account creation timestamp

### Post
- `id`: Unique identifier (UUID)
- `user_id`: Foreign key to User
- `content`: Post content text
- `likes`: Number of likes
- `created_at`: Post creation timestamp

### PostLike
- `id`: Unique identifier (UUID)
- `user_id`: Foreign key to User
- `post_id`: Foreign key to Post
- `created_at`: Like timestamp

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Example API Usage

### Register a new user:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword",
    "displayName": "John Doe"
  }'
```

### Login:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword"
  }'
```

### Create a post:
```bash
curl -X POST http://localhost:5000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "content": "Hello, world! This is my first post."
  }'
```

## Development

- The application runs in debug mode by default
- Database is automatically created on first run
- CORS is enabled for frontend development
- All endpoints except registration, login, and health check require authentication

## Security Notes

- Change the JWT secret key in production
- Use environment variables for sensitive configuration
- Consider using PostgreSQL for production instead of SQLite
- Implement rate limiting for production use
- Add input validation and sanitization
