# Move .env out of the way temporarily
Move-Item .env .env.bak -ErrorAction SilentlyContinue

Write-Host "==================== STEP 1: No ADMIN_KEY ===================="
& "I:\QYNTARA AI\test_env_full\Scripts\python.exe" -m uvicorn backend.main:app
Write-Host ""

Write-Host "==================== STEP 2: Boot with ADMIN_KEY ===================="
$env:ADMIN_KEY="test1234"
$process = Start-Process "I:\QYNTARA AI\test_env_full\Scripts\python.exe" -ArgumentList "-m uvicorn backend.main:app --port 8002" -PassThru -NoNewWindow
Start-Sleep -Seconds 5
Write-Host ""

Write-Host "==================== STEP 3: curl GET /stats ===================="
curl.exe -i -s -X GET http://localhost:8002/stats
Write-Host "`n"

Write-Host "==================== STEP 4: curl POST /login ===================="
$jsonResp = curl.exe -s -X POST http://localhost:8002/login -H "Content-Type: application/json" -d '{\"api_key\": \"test1234\"}'
Write-Host $jsonResp
Write-Host "`n"

Write-Host "==================== JWT Decode ===================="
$token = ($jsonResp | ConvertFrom-Json).access_token
if ($token) {
    $parts = $token.Split(".")
    if ($parts.Length -ge 2) {
        $payload = $parts[1]
        $padding = "=" * (4 - ($payload.Length % 4))
        $payloadB64 = $payload + $padding
        $decoded = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($payloadB64))
        Write-Host "Decoded payload:"
        Write-Host $decoded
    }
}

# Cleanup
Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
Move-Item .env.bak .env -ErrorAction SilentlyContinue
