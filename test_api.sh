#!/bin/bash
# Bash script to test the API endpoints
# Make sure the API is running first!

BASE_URL="http://localhost:8000"

echo "=== Testing Organization Management API ==="
echo ""

# Test 1: Health Check
echo "1. Testing Health Endpoint..."
if curl -s "$BASE_URL/health" | grep -q "healthy"; then
    echo "   ✓ Health check passed"
else
    echo "   ✗ Health check failed. Is the API running?"
    exit 1
fi
echo ""

# Test 2: Create Organization
echo "2. Creating Organization..."
ORG_NAME="TestOrg_$(date +%Y%m%d%H%M%S)"
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/org/create" \
  -H "Content-Type: application/json" \
  -d "{
    \"organization_name\": \"$ORG_NAME\",
    \"email\": \"admin@testorg.com\",
    \"password\": \"securepass123\"
  }")

if echo "$CREATE_RESPONSE" | grep -q "created successfully"; then
    echo "   ✓ Organization created: $ORG_NAME"
    COLLECTION_NAME=$(echo "$CREATE_RESPONSE" | grep -o '"collection_name":"[^"]*' | cut -d'"' -f4)
    echo "   Collection: $COLLECTION_NAME"
else
    echo "   ✗ Failed to create organization"
    echo "$CREATE_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Login
echo "3. Logging in as Admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@testorg.com",
    "password": "securepass123"
  }')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo "   ✓ Login successful"
    echo "   Token: ${TOKEN:0:20}..."
else
    echo "   ✗ Login failed"
    echo "$LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Test 4: Get Organization
echo "4. Getting Organization Details..."
ENCODED_ORG_NAME=$(echo "$ORG_NAME" | sed 's/ /%20/g')
GET_RESPONSE=$(curl -s "$BASE_URL/org/get?organization_name=$ENCODED_ORG_NAME")

if echo "$GET_RESPONSE" | grep -q "$ORG_NAME"; then
    echo "   ✓ Organization retrieved: $ORG_NAME"
else
    echo "   ✗ Failed to get organization"
    echo "$GET_RESPONSE"
fi
echo ""

# Test 5: Update Organization
echo "5. Updating Organization..."
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/org/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"organization_name\": \"$ORG_NAME\",
    \"email\": \"newadmin@testorg.com\"
  }")

if echo "$UPDATE_RESPONSE" | grep -q "updated successfully"; then
    echo "   ✓ Organization updated"
    NEW_EMAIL=$(echo "$UPDATE_RESPONSE" | grep -o '"email":"[^"]*' | head -1 | cut -d'"' -f4)
    echo "   New email: $NEW_EMAIL"
else
    echo "   ✗ Failed to update organization"
    echo "$UPDATE_RESPONSE"
fi
echo ""

# Test 6: Delete Organization
echo "6. Deleting Organization..."
DELETE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/org/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"organization_name\": \"$ORG_NAME\"
  }")

if echo "$DELETE_RESPONSE" | grep -q "deleted successfully"; then
    echo "   ✓ Organization deleted"
else
    echo "   ✗ Failed to delete organization"
    echo "$DELETE_RESPONSE"
fi
echo ""

echo "=== All Tests Completed ==="

