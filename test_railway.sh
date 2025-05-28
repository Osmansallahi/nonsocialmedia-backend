#!/bin/bash

# Test script for Railway deployment
echo "Testing Railway deployment at: https://web-production-7c9d.up.railway.app"

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
    if [[ -n "$TOKEN" ]]; then
        echo -e "${GREEN}✓ JWT token received${NC}"
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

echo -e "\n${YELLOW}3. Testing profile retrieval...${NC}"
PROFILE_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/auth/profile" \
    -H "Authorization: Bearer ${TOKEN}")

if echo "$PROFILE_RESPONSE" | grep -q "user"; then
    echo -e "${GREEN}✓ Profile retrieval successful${NC}"
else
    echo -e "${RED}✗ Profile retrieval failed${NC}"
    echo "$PROFILE_RESPONSE"
fi

echo -e "\n${YELLOW}4. Testing image upload endpoint (without file)...${NC}"
UPLOAD_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/profile-picture" \
    -H "Authorization: Bearer ${TOKEN}")

if echo "$UPLOAD_RESPONSE" | grep -q "No file part"; then
    echo -e "${GREEN}✓ Upload endpoint accessible (expected 'No file part' error)${NC}"
else
    echo -e "${RED}✗ Upload endpoint issue${NC}"
    echo "$UPLOAD_RESPONSE"
fi

echo -e "\n${YELLOW}5. Testing static file serving...${NC}"
# Test if we can access the uploads directory (should return 404 for non-existent file)
STATIC_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/uploads/profile_pictures/nonexistent.jpg")

if [[ "$STATIC_RESPONSE" == "404" ]]; then
    echo -e "${GREEN}✓ Static file serving configured (404 for non-existent file)${NC}"
else
    echo -e "${RED}✗ Static file serving issue (HTTP: ${STATIC_RESPONSE})${NC}"
fi

echo -e "\n${GREEN}✓ Basic deployment tests completed!${NC}"
echo -e "\n${YELLOW}Notes:${NC}"
echo "- Image uploads will work but files will be lost on Railway restarts"
echo "- Consider using cloud storage (Cloudinary, AWS S3) for production"
echo "- Set BASE_URL environment variable in Railway dashboard for proper file URLs"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Set environment variables in Railway dashboard (see RAILWAY_DEPLOYMENT.md)"
echo "2. Test with actual image upload from your frontend"
echo "3. Consider implementing cloud storage for production use"
