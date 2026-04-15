Write-Host "=== DRIVE STATUS ==="
Get-PSDrive C, F | ForEach-Object {
    Write-Host "$($_.Name): Free $([math]::Round($_.Free/1GB, 2)) GB | Used $([math]::Round($_.Used/1GB, 2)) GB"
}

Write-Host ""
Write-Host "=== OLLAMA STATUS ==="
$env:OLLAMA_MODELS = "F:\ollama_models"
Write-Host "OLLAMA_MODELS = $env:OLLAMA_MODELS"
Write-Host ""
Write-Host "Models:"
ollama list

Write-Host ""
Write-Host "=== OLLAMA FILES ON F: ==="
if (Test-Path "F:\ollama_models") {
    $size = (Get-ChildItem "F:\ollama_models" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "Total in F:\ollama_models: $([math]::Round($size, 2)) GB"
    Get-ChildItem "F:\ollama_models\manifests\registry.ollama.ai\library" -Directory | ForEach-Object {
        Write-Host "  - $($_.Name)"
    }
}
