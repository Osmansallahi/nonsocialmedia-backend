#!/usr/bin/env python3
"""
Comprehensive test for profile image upload with database storage
"""

import requests
import json
import base64
import io
from PIL import Image
import tempfile
import os

# Test configuration
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

def create_test_image():
    """Create a test image for upload"""
    # Create a simple test image
    img = Image.new('RGB', (200, 200), color='red')
    
    # Add some content to make it more realistic
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    try:
        # Try to use a font if available
        font = ImageFont.load_default()
        draw.text((50, 100), "TEST", fill='white', font=font)
    except:
        draw.text((50, 100), "TEST", fill='white')
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file.name, 'JPEG', quality=85)
    return temp_file.name

def test_health_check():
    """Test if the API is running"""
    print("1. Testing health check...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API is healthy: {data['status']}")
            print(f"✓ Storage type: {data['storage_type']}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Is the Flask app running?")
        return False

def test_user_registration():
    """Register a test user"""
    print("\n2. Testing user registration...")
    user_data = {
        "username": "testuser_upload",
        "email": "testuser@example.com",
        "password": "testpass123",
        "displayName": "Test User Upload"
    }
    
    response = requests.post(f"{API_URL}/auth/register", json=user_data)
    if response.status_code == 201:
        data = response.json()
        print(f"✓ User registered: {data['user']['username']}")
        return data['access_token'], data['user']['id']
    else:
        print(f"✗ Registration failed: {response.text}")
        return None, None

def test_image_upload(token, user_id):
    """Test profile image upload"""
    print("\n3. Testing profile image upload...")
    
    # Create test image
    test_image_path = create_test_image()
    
    try:
        # Upload image
        headers = {'Authorization': f'Bearer {token}'}
        
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{API_URL}/auth/profile-picture", 
                                   headers=headers, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Image uploaded successfully")
            print(f"✓ Profile picture URL: {data['user']['profilePicture']}")
            return True
        else:
            print(f"✗ Upload failed: {response.text}")
            return False
            
    finally:
        # Clean up test image
        os.unlink(test_image_path)

def test_image_serving(user_id):
    """Test serving the uploaded image"""
    print("\n4. Testing image serving...")
    
    response = requests.get(f"{API_URL}/auth/profile-picture/{user_id}")
    
    if response.status_code == 200:
        print(f"✓ Image served successfully")
        print(f"✓ Content type: {response.headers.get('content-type')}")
        print(f"✓ Image size: {len(response.content)} bytes")
        
        # Verify it's a valid image
        try:
            img = Image.open(io.BytesIO(response.content))
            print(f"✓ Valid image: {img.format} {img.size}")
            return True
        except Exception as e:
            print(f"✗ Invalid image data: {e}")
            return False
    else:
        print(f"✗ Image serving failed: {response.text}")
        return False

def test_profile_update(token):
    """Test getting updated profile"""
    print("\n5. Testing profile retrieval...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{API_URL}/auth/profile", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        profile_pic_url = data['user']['profilePicture']
        print(f"✓ Profile retrieved successfully")
        print(f"✓ Profile picture URL: {profile_pic_url}")
        
        # Check if URL points to our API endpoint
        if profile_pic_url.startswith('/api/auth/profile-picture/'):
            print("✓ Profile picture URL points to database storage endpoint")
            return True
        else:
            print("✗ Profile picture URL doesn't use database storage")
            return False
    else:
        print(f"✗ Profile retrieval failed: {response.text}")
        return False

def main():
    """Run all tests"""
    print("=== Profile Image Upload Test (Database Storage) ===")
    
    # Check if API is running
    if not test_health_check():
        print("\nPlease start the Flask application first:")
        print("cd /home/othmansalahi/Documents/Webdev/backend && python app.py")
        return
    
    # Register user and get token
    token, user_id = test_user_registration()
    if not token:
        return
    
    # Test image upload
    if not test_image_upload(token, user_id):
        return
    
    # Test image serving
    if not test_image_serving(user_id):
        return
    
    # Test profile retrieval
    if not test_profile_update(token):
        return
    
    print("\n✓ All tests passed! Database storage is working correctly.")
    print("\nBenefits of database storage:")
    print("- ✓ No file system dependencies")
    print("- ✓ Works on Railway and other platforms")
    print("- ✓ Images persist through deployments")
    print("- ✓ No ephemeral storage issues")

if __name__ == "__main__":
    main()
