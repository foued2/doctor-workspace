taskkill /F /IM ollama.exe 2>$null
Start-Sleep -Seconds 2
$env:OLLAMA_MODELS = "F:\ollama_models"
$env:OLLAMA_HOST = "127.0.0.1:11435"
Write-Host "Pulling phi3 to $env:OLLAMA_MODELS..."
ollama pull phi3
Write-Host "Done. Verifying..."
ollama list
