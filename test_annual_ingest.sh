#!/bin/bash

# Test script for annual company data ingestion
# Tests the new /ingest/company/{symbol} endpoint with annual frequency

echo "🧪 Testing Annual Company Data Ingestion"
echo "========================================"

BASE_URL="http://127.0.0.1:8000"

# Test 1: Microsoft - 10 years annual
echo -e "\n📊 Test 1: Microsoft (MSFT) - 10 years annual data"
echo "curl \"$BASE_URL/ingest/company/MSFT?years=10&frequency=annual\""
curl -s "$BASE_URL/ingest/company/MSFT?years=10&frequency=annual" | python3 -m json.tool

# Test 2: Apple - 10 years annual
echo -e "\n📊 Test 2: Apple (AAPL) - 10 years annual data"
echo "curl \"$BASE_URL/ingest/company/AAPL?years=10&frequency=annual\""
curl -s "$BASE_URL/ingest/company/AAPL?years=10&frequency=annual" | python3 -m json.tool

# Test 3: Google - 5 years quarterly (for comparison)
echo -e "\n📊 Test 3: Google (GOOGL) - 5 years quarterly data"
echo "curl \"$BASE_URL/ingest/company/GOOGL?years=5&frequency=quarterly\""
curl -s "$BASE_URL/ingest/company/GOOGL?years=5&frequency=quarterly" | python3 -m json.tool

# Test 4: Retrieve stored data
echo -e "\n📊 Test 4: Retrieve stored Microsoft data"
echo "curl \"$BASE_URL/data/company/MSFT\""
curl -s "$BASE_URL/data/company/MSFT" | python3 -m json.tool | head -20

# Test 5: Test with invalid parameters
echo -e "\n📊 Test 5: Invalid frequency parameter"
echo "curl \"$BASE_URL/ingest/company/MSFT?years=10&frequency=monthly\""
curl -s "$BASE_URL/ingest/company/MSFT?years=10&frequency=monthly" | python3 -m json.tool

# Test 6: Test with years > 20 (should cap at 20)
echo -e "\n📊 Test 6: Years > 20 (should cap at 20)"
echo "curl \"$BASE_URL/ingest/company/MSFT?years=25&frequency=annual\""
curl -s "$BASE_URL/ingest/company/MSFT?years=25&frequency=annual" | python3 -m json.tool

echo -e "\n✅ Testing completed!" 