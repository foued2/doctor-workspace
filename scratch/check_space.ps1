# Check Ollama models directory
$ollamaPath = "$env:USERPROFILE\.ollama\models"
if (Test-Path $ollamaPath) {
    $size = (Get-ChildItem $ollamaPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "Ollama models: $([math]::Round($size, 2)) GB"
} else {
    Write-Host "Ollama models folder not found at $ollamaPath"
}

# Check temp files
$tempPath = "$env:TEMP"
$oldFiles = Get-ChildItem -Path $tempPath -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-3) }
$tempSize = ($oldFiles | Measure-Object -Property Length -Sum).Sum / 1GB
Write-Host "Old temp files: $([math]::Round($tempSize, 2)) GB"

# Check Windows temp
$winTemp = "C:\Windows\Temp"
if (Test-Path $winTemp) {
    $winTempSize = (Get-ChildItem $winTemp -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "Windows temp: $([math]::Round($winTempSize, 2)) GB"
}

# Check Ollama manifest download progress
$ollamaData = "$env:USERPROFILE\AppData\Local\Ollama"
if (Test-Path $ollamaData) {
    $dataSize = (Get-ChildItem $ollamaData -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "Ollama app data: $([math]::Round($dataSize, 2)) GB"
}
