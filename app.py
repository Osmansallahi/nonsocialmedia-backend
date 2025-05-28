from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import uuid
from PIL import Image
import base64
import io
import tempfile

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
config_name = os.environ.get('FLASK_ENV', 'development')
if config_name == 'production':
    from config import ProductionConfig
    app.config.from_object(ProductionConfig)
else:
    from config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)

# File upload configuration (for validation only)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image_to_base64(file, max_size=(300, 300)):
    """Process uploaded image and convert to base64"""
    try:
        # Open the image
        img = Image.open(file)
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize maintaining aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        
        # Encode to base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/jpeg;base64,{img_base64}"
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def get_base_url():
    """Get the base URL for the application"""
    return app.config.get('BASE_URL', os.environ.get('BASE_URL', 'http://localhost:5000'))

def ensure_upload_directory():
    """Ensure upload directory exists and is writable"""
    upload_dir = app.config['UPLOAD_FOLDER']
    try:
        os.makedirs(upload_dir, exist_ok=True)
        # Test if directory is writable
        test_file = os.path.join(upload_dir, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except Exception as e:
        print(f"Error creating/accessing upload directory: {e}")
        # On Railway, if we can't create the upload directory, try a temp directory
        if os.environ.get('RAILWAY_ENVIRONMENT'):
            try:
                temp_dir = tempfile.mkdtemp(prefix='uploads_')
                app.config['UPLOAD_FOLDER'] = temp_dir
                print(f"Using temporary upload directory: {temp_dir}")
                return True
            except Exception as temp_e:
                print(f"Failed to create temp directory: {temp_e}")
                return False
        return False

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']), supports_credentials=True)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, default='Hello! I just joined this amazing social platform.')
    profile_picture = db.Column(db.Text, default='https://images.unsplash.com/photo-1535268647677-300dbf3d78d1?w=150&h=150&fit=crop&crop=face')
    profile_picture_data = db.Column(db.Text, nullable=True)  # Base64 encoded image data
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'displayName': self.display_name,
            'bio': self.bio,
            'profilePicture': self.profile_picture,
            'followersCount': self.followers_count,
            'followingCount': self.following_count
        }

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='posts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'author': {
                'username': self.user.username,
                'displayName': self.user.display_name,
                'profilePicture': self.user.profile_picture
            },
            'content': self.content,
            'timestamp': self.created_at.isoformat() + 'Z',  # Add Z to indicate UTC
            'likes': self.likes,
            'isLiked': False,  # This should be determined based on current user
            'comments': []  # Comments implementation can be added later
        }

class PostLike(db.Model):
    __tablename__ = 'post_likes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.String(36), db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a user can only like a post once
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id'),)

# Create tables and setup database
with app.app_context():
    db.create_all()
    
    # Print configuration info for debugging
    if app.config.get('DEBUG'):
        print(f"Base URL: {get_base_url()}")
        print(f"Environment: {app.config.get('FLASK_ENV', 'unknown')}")
        print("Using database storage for profile pictures")

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'displayName']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        username = data['username'].lower().strip()
        email = data['email'].lower().strip()
        password = data['password']
        display_name = data['displayName'].strip()
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=username,
            email=email,
            display_name=display_name,
            bio=data.get('bio', 'Hello! I just joined this amazing social platform.'),
            profile_picture=data.get('profilePicture', 'https://images.unsplash.com/photo-1535268647677-300dbf3d78d1?w=150&h=150&fit=crop&crop=face')
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        username_or_email = data.get('username', '').lower().strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({'error': 'Username/email and password are required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update user fields
        if 'displayName' in data:
            user.display_name = data['displayName'].strip()
        if 'bio' in data:
            user.bio = data['bio']
        if 'profilePicture' in data:
            user.profile_picture = data['profilePicture']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

# Post Routes
@app.route('/api/posts', methods=['GET'])
@jwt_required()
def get_posts():
    try:
        current_user_id = get_jwt_identity()
        posts = Post.query.order_by(Post.created_at.desc()).all()
        
        posts_data = []
        for post in posts:
            post_dict = post.to_dict()
            # Check if current user liked this post
            like = PostLike.query.filter_by(user_id=current_user_id, post_id=post.id).first()
            post_dict['isLiked'] = bool(like)
            posts_data.append(post_dict)
        
        return jsonify({'posts': posts_data}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        post = Post(
            user_id=current_user_id,
            content=content
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'message': 'Post created successfully',
            'post': post.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/posts/<post_id>/like', methods=['POST'])
@jwt_required()
def toggle_like(post_id):
    try:
        current_user_id = get_jwt_identity()
        
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Check if user already liked the post
        existing_like = PostLike.query.filter_by(user_id=current_user_id, post_id=post_id).first()
        
        if existing_like:
            # Unlike the post
            db.session.delete(existing_like)
            post.likes = max(0, post.likes - 1)
            is_liked = False
        else:
            # Like the post
            like = PostLike(user_id=current_user_id, post_id=post_id)
            db.session.add(like)
            post.likes += 1
            is_liked = True
        
        db.session.commit()
        
        return jsonify({
            'message': 'Like toggled successfully',
            'likes': post.likes,
            'isLiked': is_liked
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

# User Routes
@app.route('/api/users/<username>', methods=['GET'])
@jwt_required()
def get_user_by_username(username):
    try:
        user = User.query.filter_by(username=username.lower()).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# File Upload Route
@app.route('/api/auth/profile-picture', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Process image and convert to base64
        base64_image = resize_image_to_base64(file)
        
        if not base64_image:
            return jsonify({'error': 'Failed to process image'}), 400
        
        # Store the base64 data in database
        user.profile_picture_data = base64_image
        user.profile_picture = f"/api/auth/profile-picture/{current_user_id}"
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error uploading profile picture: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Serve profile pictures from database
@app.route('/api/auth/profile-picture/<user_id>', methods=['GET'])
def get_profile_picture(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user or not user.profile_picture_data:
            # Return default image or 404
            return jsonify({'error': 'Profile picture not found'}), 404
        
        # Extract base64 data (remove data:image/jpeg;base64, prefix)
        if user.profile_picture_data.startswith('data:image/jpeg;base64,'):
            base64_data = user.profile_picture_data.split(',')[1]
        else:
            base64_data = user.profile_picture_data
        
        # Decode base64 to bytes
        try:
            image_data = base64.b64decode(base64_data)
        except Exception as e:
            print(f"Error decoding base64: {e}")
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Create response with image data
        from flask import Response
        response = Response(image_data, mimetype='image/jpeg')
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        
        return response
        
    except Exception as e:
        print(f"Error serving profile picture: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.utcnow().isoformat(),
        'storage_type': 'database',
        'base_url': get_base_url()
    }), 200

# Debug endpoint (development only)
@app.route('/api/debug/config', methods=['GET'])
def debug_config():
    if app.config.get('FLASK_ENV') != 'development':
        return jsonify({'error': 'Debug endpoint only available in development'}), 403
    
    return jsonify({
        'flask_env': app.config.get('FLASK_ENV'),
        'base_url': get_base_url(),
        'max_content_length': app.config.get('MAX_CONTENT_LENGTH'),
        'storage_type': 'database'
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)