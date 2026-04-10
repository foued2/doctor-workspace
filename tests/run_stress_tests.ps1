# Stress Test Runner for Multi-Feature Scorer
# ============================================
# This script runs the stress tests for the new multi-feature scorer.
#
# Prerequisites:
# - Python 3.8+ installed and in PATH
# - If Python is not in PATH, update the PYTHON_CMD variable below
#
# Usage:
# .\run_stress_tests.ps1

$PYTHON_CMD = "python"  # Change to full path if needed, e.g., "C:\Python39\python.exe"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Multi-Feature Scorer Stress Tests" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = Join-Path $PSScriptRoot "leetcode-tools\stress_test_scorer.py"

if (-not (Test-Path $scriptPath)) {
    Write-Host "ERROR: Stress test file not found at: $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "Running stress tests...`n" -ForegroundColor Yellow

& $PYTHON_CMD $scriptPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nAll stress tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "`nSome stress tests failed. Check the output above for details." -ForegroundColor Red
}

exit $LASTEXITCODE
