#!/bin/bash

# Simple test script for the Social Media Backend API
# Make sure the Flask server is running before executing this script

BASE_URL="http://localhost:5000"
echo "🚀 Testing Social Media Backend API"
echo "=================================="

# Test health endpoint
echo "📊 Testing health endpoint..."
curl -s -X GET "$BASE_URL/api/health" | python3 -m json.tool
echo -e "\n"

# Test user registration
echo "👤 Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demouser",
    "email": "demo@example.com",
    "password": "demopassword123",
    "displayName": "Demo User",
    "bio": "I am a demo user testing this awesome platform!"
  }')

echo "$REGISTER_RESPONSE" | python3 -m json.tool
TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
echo -e "\n"

# Test user login
echo "🔐 Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demouser",
    "password": "demopassword123"
  }')

echo "$LOGIN_RESPONSE" | python3 -m json.tool
echo -e "\n"

# Test creating posts
echo "📝 Testing post creation..."
curl -s -X POST "$BASE_URL/api/posts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "content": "🎉 Welcome to my profile! This is my first post on this amazing social platform!"
  }' | python3 -m json.tool
echo -e "\n"

curl -s -X POST "$BASE_URL/api/posts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "content": "Just had an amazing day! 🌟 The weather is beautiful and I am loving this new social platform. Can not wait to connect with more people!"
  }' | python3 -m json.tool
echo -e "\n"

# Test getting all posts
echo "📋 Testing getting all posts..."
POSTS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/posts" \
  -H "Authorization: Bearer $TOKEN")

echo "$POSTS_RESPONSE" | python3 -m json.tool

# Extract first post ID for like test
POST_ID=$(echo "$POSTS_RESPONSE" | python3 -c "import sys, json; posts = json.load(sys.stdin)['posts']; print(posts[0]['id'] if posts else '')" 2>/dev/null)
echo -e "\n"

if [ ! -z "$POST_ID" ]; then
  # Test liking a post
  echo "❤️ Testing post like functionality..."
  curl -s -X POST "$BASE_URL/api/posts/$POST_ID/like" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
  echo -e "\n"
  
  # Test unliking the same post
  echo "💔 Testing post unlike functionality..."
  curl -s -X POST "$BASE_URL/api/posts/$POST_ID/like" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
  echo -e "\n"
fi

# Test getting user profile
echo "👨‍💻 Testing user profile retrieval..."
curl -s -X GET "$BASE_URL/api/auth/profile" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo -e "\n"

# Test updating user profile
echo "✏️ Testing user profile update..."
curl -s -X PUT "$BASE_URL/api/auth/profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "displayName": "Demo User (Updated)",
    "bio": "I am a demo user who just updated their profile! This platform is fantastic! 🚀",
    "profilePicture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face"
  }' | python3 -m json.tool
echo -e "\n"

echo "✅ API testing completed!"
echo "========================"
