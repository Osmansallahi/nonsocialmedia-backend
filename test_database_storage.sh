#!/bin/bash

# Test script for Database-based Image Storage
echo "Testing Database-based Profile Picture Storage"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="https://web-production-7c9d.up.railway.app"

echo -e "${YELLOW}1. Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "${BASE_URL}/api/health")
if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo -e "${RED}✗ Health check failed${NC}"
    exit 1
fi

echo -e "\n${YELLOW}2. Testing user registration...${NC}"
# Generate random user data
RANDOM_ID=$RANDOM
USERNAME="testuser${RANDOM_ID}"
EMAIL="test${RANDOM_ID}@example.com"

REGISTER_DATA="{
    \"username\": \"${USERNAME}\",
    \"email\": \"${EMAIL}\",
    \"password\": \"testpass123\",
    \"displayName\": \"Test User ${RANDOM_ID}\"
}"

REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "$REGISTER_DATA")

if echo "$REGISTER_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ User registration successful${NC}"
    TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    USER_ID=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['id'])" 2>/dev/null)
    if [[ -n "$TOKEN" ]]; then
        echo -e "${GREEN}✓ JWT token received${NC}"
        echo -e "${GREEN}✓ User ID: ${USER_ID}${NC}"
    else
        echo -e "${RED}✗ No JWT token in response${NC}"
        echo "$REGISTER_RESPONSE"
        exit 1
    fi
else
    echo -e "${RED}✗ User registration failed${NC}"
    echo "$REGISTER_RESPONSE"
    exit 1
fi

echo -e "\n${YELLOW}3. Testing database-based image upload endpoint...${NC}"
UPLOAD_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/profile-picture" \
    -H "Authorization: Bearer ${TOKEN}")

if echo "$UPLOAD_RESPONSE" | grep -q "No file part"; then
    echo -e "${GREEN}✓ Database upload endpoint accessible (expected 'No file part' error)${NC}"
else
    echo -e "${RED}✗ Database upload endpoint issue${NC}"
    echo "$UPLOAD_RESPONSE"
fi

echo -e "\n${YELLOW}4. Testing database image serving endpoint...${NC}"
# Test if we can access the profile picture endpoint (should return 404 for no image)
IMAGE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/auth/profile-picture/${USER_ID}")

if [[ "$IMAGE_RESPONSE" == "404" ]]; then
    echo -e "${GREEN}✓ Database image serving endpoint working (404 for no uploaded image)${NC}"
else
    echo -e "${RED}✗ Database image serving endpoint issue (HTTP: ${IMAGE_RESPONSE})${NC}"
fi

echo -e "\n${GREEN}✓ Database storage tests completed!${NC}"
echo -e "\n${YELLOW}Benefits of Database Storage:${NC}"
echo "✓ No file system dependencies"
echo "✓ Works perfectly on Railway and other platforms"
echo "✓ Images are stored securely in PostgreSQL database"
echo "✓ No issues with ephemeral storage"
echo "✓ Images persist through deployments and restarts"

echo -e "\n${YELLOW}How it works:${NC}"
echo "1. Images are uploaded and processed (resized, optimized)"
echo "2. Converted to base64 and stored in 'profile_picture_data' column"
echo "3. Served directly from database via /api/auth/profile-picture/{user_id}"
echo "4. Profile picture URL points to the API endpoint"

echo -e "\n${YELLOW}Database Schema:${NC}"
echo "- Added 'profile_picture_data' TEXT column to users table"
echo "- Stores base64 encoded JPEG data"
echo "- profile_picture field now contains API endpoint URL"
