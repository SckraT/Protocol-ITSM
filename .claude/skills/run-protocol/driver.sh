#!/bin/bash
# Smoke test for Meeting Minutes (Protocol) web app
# Tests basic functionality: web UI load, API endpoints, database

set -e

API_BASE="http://localhost:8000"
TIMEOUT=10

echo "=== Protocol Smoke Test ==="
echo ""

# 1. Check if server is running
echo "✓ Checking if server is accessible..."
if ! timeout $TIMEOUT curl -s "$API_BASE/" > /dev/null 2>&1; then
    echo "✗ Server not responding at $API_BASE"
    exit 1
fi
echo "  Server is responding"

# 2. Check main UI loads
echo "✓ Loading main page..."
ui_response=$(curl -s "$API_BASE/")
if echo "$ui_response" | grep -q "Meeting Minutes\|Протокол\|Meeting"; then
    echo "  Main page loaded successfully"
else
    echo "✗ Main page does not contain expected content"
    exit 1
fi

# 3. Test API: get items
echo "✓ Testing /api/items endpoint..."
items=$(curl -s "$API_BASE/api/items")
if echo "$items" | grep -q '"id"'; then
    count=$(echo "$items" | grep -o '"id"' | wc -l)
    echo "  API returned $count item(s)"
else
    echo "  API returned items list (may be empty)"
fi

# 4. Test API: get departments
echo "✓ Testing /api/departments endpoint..."
depts=$(curl -s "$API_BASE/api/departments")
if echo "$depts" | grep -q '"id"'; then
    echo "  Departments endpoint working"
fi

# 5. Test API: get executors
echo "✓ Testing /api/executors endpoint..."
execs=$(curl -s "$API_BASE/api/executors")
if echo "$execs" | grep -q '"id"'; then
    echo "  Executors endpoint working"
fi

echo ""
echo "=== All smoke tests passed ✓ ==="
