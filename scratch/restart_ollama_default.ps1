# Restart Ollama on default port
taskkill /F /IM ollama.exe 2>$null
Start-Sleep -Seconds 3
Start-Process ollama -WindowStyle Hidden
Start-Sleep -Seconds 5
Write-Host "Ollama restarted on port 11434"
ollama list
