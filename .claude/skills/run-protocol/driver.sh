#!/bin/bash
# Smoke test for Meeting Minutes (Protocol) web app
# Tests basic functionality: web UI load, API endpoints, database

set -e

API_BASE="http://localhost:8000"
TIMEOUT=10

echo "=== Protocol Smoke Test ==="
echo ""

# 1. Health check
echo "✓ Checking /health endpoint..."
if ! timeout $TIMEOUT curl -sf "$API_BASE/health" > /dev/null 2>&1; then
    echo "✗ Health check failed at $API_BASE/health"
    exit 1
fi
health=$(curl -s "$API_BASE/health")
if echo "$health" | grep -q '"status"'; then
    echo "  Health: $health"
else
    echo "✗ /health did not return expected payload"
    exit 1
fi

# 2. Check main UI loads (Svelte SPA)
echo "✓ Loading main page..."
ui_response=$(curl -s "$API_BASE/")
if echo "$ui_response" | grep -q "Протокол\|sveltekit\|<!doctype html>"; then
    echo "  Main page (SPA) loaded successfully"
else
    echo "✗ Main page does not contain expected content"
    exit 1
fi

# 3. Test API: get items (v2 returns PaginatedResponse: {items, total, page, page_size})
echo "✓ Testing /api/items endpoint..."
items=$(curl -s "$API_BASE/api/items")
if echo "$items" | grep -q '"total"\|"items"'; then
    echo "  API returned paginated items response"
else
    echo "✗ /api/items did not return expected PaginatedResponse shape"
    exit 1
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
