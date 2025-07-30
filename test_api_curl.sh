git #!/bin/bash

# Test script for Hugging Face Space AI Singer API
API_URL="https://rocketlaunchers-ai_singer.hf.space"

echo "🧪 Testing Hugging Face Space AI Singer API"
echo "=========================================="
echo "🌐 API URL: $API_URL"
echo ""

# Test 1: Health Check
echo "🏥 Testing health endpoint..."
curl -s "$API_URL/health" | jq '.' 2>/dev/null || curl -s "$API_URL/health"
echo ""

# Test 2: Root endpoint
echo "🏠 Testing root endpoint..."
curl -s "$API_URL/" | jq '.' 2>/dev/null || curl -s "$API_URL/"
echo ""

# Test 3: Simple singing generation
echo "🎤 Testing simple singing generation..."
curl -s -X POST "$API_URL/generate-singing" \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics": "Hello world, this is a test",
    "voice_style": "pop",
    "mood": "happy",
    "include_music": false,
    "tts_engine": "auto"
  }' | jq '.' 2>/dev/null || curl -s -X POST "$API_URL/generate-singing" \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics": "Hello world, this is a test",
    "voice_style": "pop",
    "mood": "happy",
    "include_music": false,
    "tts_engine": "auto"
  }'

echo ""
echo "✅ Test completed!"
echo "💡 If you see JSON responses above, your API is working!" 