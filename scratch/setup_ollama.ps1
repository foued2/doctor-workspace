# Set Ollama environment permanently and restart

# Set system environment variable (requires admin)
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "F:\ollama_models", "User")

# Set for current session
$env:OLLAMA_MODELS = "F:\ollama_models"

Write-Host "OLLAMA_MODELS set to: $env:OLLAMA_MODELS"
Write-Host ""

# Kill any existing ollama
taskkill /F /IM ollama.exe 2>$null
Start-Sleep -Seconds 3

# Start Ollama with env var
Write-Host "Starting Ollama..."
$proc = Start-Process -FilePath "ollama" -ArgumentList "serve" -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 8

Write-Host ""
Write-Host "Available models:"
ollama list

Write-Host ""
Write-Host "Testing phi3..."
ollama run phi3 "Hello" --verbose 2>&1 | Select-Object -First 5
