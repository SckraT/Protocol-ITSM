#!/bin/bash
# Smoke test for Meeting Minutes (Protocol) web app v2.1
# Tests: health, SPA, auth (login), API endpoints with Bearer token

set -e

API_BASE="http://localhost:8000"
TIMEOUT=10

echo "=== Protocol Smoke Test v2.1 ==="
echo ""

# 1. Health check (не требует авторизации)
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

# 3. API без токена должно вернуть 401
echo "✓ Checking auth guard (expect 401 without token)..."
status_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/items")
if [ "$status_code" = "401" ]; then
    echo "  Got 401 as expected — auth guard works"
else
    echo "✗ Expected 401, got $status_code"
    exit 1
fi

# 4. Login: получаем access-токен
echo "✓ Testing login (admin/admin)..."
login_resp=$(curl -s -X POST "$API_BASE/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin"}')
TOKEN=$(echo "$login_resp" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -z "$TOKEN" ]; then
    echo "✗ Login failed. Response: $login_resp"
    exit 1
fi
echo "  Login successful, got access_token"

# 5. GET /api/items с токеном — должен вернуть PaginatedResponse
echo "✓ Testing /api/items with Bearer token..."
items=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/api/items")
if echo "$items" | grep -q '"total"\|"items"'; then
    echo "  API returned paginated items response"
else
    echo "✗ /api/items did not return expected PaginatedResponse shape"
    exit 1
fi

# 6. GET /api/departments с токеном
echo "✓ Testing /api/departments..."
depts=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/api/departments")
if echo "$depts" | grep -q '\[\|"id"'; then
    echo "  Departments endpoint working"
fi

# 7. GET /api/executors с токеном
echo "✓ Testing /api/executors..."
execs=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/api/executors")
if echo "$execs" | grep -q '\[\|"id"'; then
    echo "  Executors endpoint working"
fi

# 8. GET /api/auth/me — проверяем возвращаемую роль
echo "✓ Testing /api/auth/me..."
me=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/api/auth/me")
if echo "$me" | grep -q '"role"'; then
    echo "  Me: $me"
else
    echo "✗ /api/auth/me failed"
    exit 1
fi

# 9. GET /api/users — должен быть доступен admin-у
echo "✓ Testing /api/users (admin only)..."
users=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/api/users")
if echo "$users" | grep -q '"username"'; then
    echo "  Users list accessible"
else
    echo "✗ /api/users failed"
    exit 1
fi

echo ""
echo "=== All smoke tests passed ✓ ==="
