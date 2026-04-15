Write-Host "=== DRIVE STATUS ==="
Get-PSDrive C, F | ForEach-Object {
    Write-Host "$($_.Name): Free $([math]::Round($_.Free/1GB, 2)) GB | Used $([math]::Round($_.Used/1GB, 2)) GB"
}

Write-Host ""
Write-Host "=== OLLAMA DOWNLOAD STATUS ==="
$env:OLLAMA_MODELS = "F:\ollama_models"
$env:OLLAMA_HOST = "127.0.0.1:11435"
if (Test-Path "F:\ollama_models") {
    $size = (Get-ChildItem "F:\ollama_models" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "Downloaded: $([math]::Round($size, 2)) GB / 2.2 GB target"
} else {
    Write-Host "F:\ollama_models not found"
}

Write-Host ""
Write-Host "=== OLLAMA LIST ==="
ollama list
