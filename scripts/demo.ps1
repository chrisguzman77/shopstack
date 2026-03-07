$base = "http://localhost:8000"

curl "$base/auth/health"
curl "$base/orders/health"

curl -X POST "$base/auth/auth/register" -H "Content-Type: application/json" -d '{"email":"demo@example.com","password":"Password123!"}'

$resp = curl -X POST "$base/auth/auth/login" -H "Content-Type: application/json" -d '{"email":"demo@example.com","password":"Password123!"}' | ConvertFrom-Json
$token = $resp.access_token

$order = curl -X POST "$base/orders/orders" -H "Authorization: Bearer $token" -H "Idempotency-Key: demo-1" -H "Content-Type: application/json" `
  -d '{"currency":"USD","items":[{"sku":"SKU1","name":"Thing","qty":1,"unit_price":999}]}' | ConvertFrom-Json

curl -X POST "$base/orders/orders/$($order.id)/pay" -H "Authorization: Bearer $token"