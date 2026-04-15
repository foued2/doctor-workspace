$env:OLLAMA_MODELS = "F:\ollama_models"
Write-Host "Starting Ollama with OLLAMA_MODELS=$env:OLLAMA_MODELS"
Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
Start-Sleep 6
Write-Host ""
Write-Host "Models available:"
ollama list
