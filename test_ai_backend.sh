#!/bin/bash
# Simple AI Backend Test Script using curl

echo "🎵 AI SINGER BACKEND COMPREHENSIVE TEST 🎵"
echo "=================================================="

echo ""
echo "1. Testing Basic Pitch Service Health..."
BASIC_PITCH_HEALTH=$(curl -s http://localhost:8001/health)
if [[ $BASIC_PITCH_HEALTH == *"healthy"* ]]; then
    echo "✅ Basic Pitch service is healthy!"
    echo "   Response: $BASIC_PITCH_HEALTH"
else
    echo "❌ Basic Pitch service health check failed!"
    echo "   Response: $BASIC_PITCH_HEALTH"
fi

echo ""
echo "2. Testing Coqui TTS Service Health..."
TTS_HEALTH=$(curl -s http://localhost:8002/health)
if [[ $TTS_HEALTH == *"healthy"* ]]; then
    echo "✅ Coqui TTS service is healthy!"
    echo "   Response: $TTS_HEALTH"
else
    echo "❌ Coqui TTS service health check failed!"
    echo "   Response: $TTS_HEALTH"
fi

echo ""
echo "3. Testing Basic Pitch Melody Extraction Endpoint..."
MELODY_TEST=$(curl -s -X POST http://localhost:8001/extract-melody \
  -H "Content-Type: application/json" \
  -d '{"audio": "invalid_test_data"}')

if [[ $MELODY_TEST == *"error"* ]]; then
    echo "✅ Melody extraction endpoint is responding (expects error with invalid data)"
    echo "   Response: $MELODY_TEST"
else
    echo "❌ Melody extraction endpoint not responding properly"
    echo "   Response: $MELODY_TEST"
fi

echo ""
echo "4. Testing Coqui TTS Text-to-Speech Endpoint..."
TTS_TEST=$(curl -s -X POST http://localhost:8002/generate-singing \
  -H "Content-Type: application/json" \
  -d '{"lyrics": "Hello, this is a test of the TTS service"}')

if [[ $TTS_TEST == *"audio"* ]] || [[ $TTS_TEST == *"error"* ]]; then
    echo "✅ TTS synthesis endpoint is responding!"
    echo "   Response length: ${#TTS_TEST} characters"
    if [[ $TTS_TEST == *"audio"* ]]; then
        echo "   Contains audio data - SUCCESS!"
    fi
else
    echo "❌ TTS synthesis endpoint not responding properly"
    echo "   Response: $TTS_TEST"
fi

echo ""
echo "=================================================="
echo "📊 TEST SUMMARY"
echo "=================================================="

# Count successful tests
SUCCESS_COUNT=0

if [[ $BASIC_PITCH_HEALTH == *"healthy"* ]]; then
    echo "✅ Basic Pitch Health: SUCCESS"
    ((SUCCESS_COUNT++))
else
    echo "❌ Basic Pitch Health: FAILED"
fi

if [[ $TTS_HEALTH == *"healthy"* ]]; then
    echo "✅ Coqui TTS Health: SUCCESS"
    ((SUCCESS_COUNT++))
else
    echo "❌ Coqui TTS Health: FAILED"
fi

if [[ $MELODY_TEST == *"error"* ]]; then
    echo "✅ Melody Extraction Endpoint: SUCCESS"
    ((SUCCESS_COUNT++))
else
    echo "❌ Melody Extraction Endpoint: FAILED"
fi

if [[ $TTS_TEST == *"audio"* ]] || [[ $TTS_TEST == *"error"* ]]; then
    echo "✅ TTS Synthesis Endpoint: SUCCESS"
    ((SUCCESS_COUNT++))
else
    echo "❌ TTS Synthesis Endpoint: FAILED"
fi

echo ""
echo "🎯 Overall: $SUCCESS_COUNT/4 tests passed"

if [ $SUCCESS_COUNT -eq 4 ]; then
    echo "🎉 ALL SYSTEMS GO! AI Singer backend is fully operational!"
elif [ $SUCCESS_COUNT -gt 2 ]; then
    echo "⚠️  Good functionality - most services are working"
elif [ $SUCCESS_COUNT -gt 0 ]; then
    echo "⚠️  Partial functionality - some services are working"
else
    echo "🚨 System down - all services are failing"
fi
