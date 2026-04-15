# Restart Ollama with correct model path

Write-Host "Stopping Ollama..."
taskkill /F /IM ollama.exe 2>$null
Start-Sleep -Seconds 3

Write-Host "Starting Ollama with F:\ollama_models..."
$env:OLLAMA_MODELS = "F:\ollama_models"
$env:OLLAMA_HOST = "127.0.0.1:11435"
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Checking models..."
ollama list
