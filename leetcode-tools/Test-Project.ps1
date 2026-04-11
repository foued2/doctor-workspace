param(
    [switch]$Quiet
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonCandidates = @(
    (Join-Path $projectRoot 'venv\Scripts\python.exe'),
    (Join-Path $projectRoot '.venv\Scripts\python.exe')
)

$python = $pythonCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $python) {
    throw "No project virtual environment was found. Expected venv or .venv."
}

if (-not $Quiet) {
    Write-Host "Using interpreter: $python"
}

& $python -m pytest tests\test_001_100.py -q
exit $LASTEXITCODE
