param(
    [ValidateSet(
        "help",
        "suggest",
        "doctor",
        "main",
        "validate-doctor",
        "doctor-tests",
        "execution-tests",
        "tests",
        "doctor-grading",
        "doctor-hardening",
        "benchmark",
        "benchmark-strict",
        "benchmark-runner",
        "falsify",
        "full-check"
    )]
    [string]$Task = "help",
    [switch]$Quiet,
    [switch]$IncludeBenchmarks,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"

function Write-Status {
    param([string]$Message)

    if (-not $Quiet) {
        Write-Host $Message
    }
}

function Get-PythonInterpreter {
    $pythonCandidates = @(
        (Join-Path $projectRoot ".venv1\Scripts\python.exe"),
        (Join-Path $projectRoot ".venv\Scripts\python.exe"),
        (Join-Path $projectRoot "venv\Scripts\python.exe")
    )

    foreach ($candidate in $pythonCandidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    throw "No project virtual environment was found. Expected .venv1, .venv, or venv."
}

function Invoke-PythonScript {
    param(
        [string]$RelativePath,
        [string[]]$Arguments = @()
    )

    $targetPath = Join-Path $projectRoot $RelativePath
    if (-not (Test-Path $targetPath)) {
        throw "Script not found: $RelativePath"
    }

    Write-Status "Running $RelativePath"
    & $script:python $targetPath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $RelativePath"
    }
}

function Invoke-UnittestSuite {
    param([string]$Pattern)

    Write-Status "Running unittest suite: $Pattern"
    & $script:python -m unittest discover -s (Join-Path $projectRoot "tests") -p $Pattern -v
    if ($LASTEXITCODE -ne 0) {
        throw "Unittest suite failed: $Pattern"
    }
}

function Test-PytestAvailable {
    $hasNativePreference = $null -ne (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue)
    $previousPreference = $false

    if ($hasNativePreference) {
        $previousPreference = $PSNativeCommandUseErrorActionPreference
        $PSNativeCommandUseErrorActionPreference = $false
    }

    try {
        & $script:python -c "import pytest" *> $null
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
    finally {
        if ($hasNativePreference) {
            $PSNativeCommandUseErrorActionPreference = $previousPreference
        }
    }
}

function Invoke-PytestTests {
    param([string[]]$Arguments = @())

    if (-not (Test-PytestAvailable)) {
        throw "pytest is not installed in the selected interpreter."
    }

    Write-Status "Running pytest suite"
    & $script:python -m pytest (Join-Path $projectRoot "tests") -v @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "pytest suite failed."
    }
}

function Show-Help {
    @"
Run-Project.ps1

Usage:
  .\Run-Project.ps1 <task> [task arguments]

Tasks:
  help                Show this help message.
  suggest             Run the LeetCode suggestor.
  doctor              Run the LeetCode doctor. Pass the problem id or doctor flags after the task.
  main                Run main.py.
  validate-doctor     Run validate_doctor.py.
  doctor-tests        Run the raw-prompt doctor unittest suite.
  execution-tests     Run the execution harness unittest suite.
  tests               Run all tests in tests/. Uses pytest when available, otherwise falls back to unittest suites.
  doctor-grading      Run test_doctor_grading.py.
  doctor-hardening    Run test_doctor_hardening.py.
  benchmark           Run doctor_attack_benchmark.py.
  benchmark-strict    Run doctor_attack_benchmark_strict.py.
  benchmark-runner    Run benchmark_runner.py.
  falsify             Run final_falsification_test.py.
  full-check          Run validator + unittest suites, and optionally the strict benchmark.

Examples:
  .\Run-Project.ps1 suggest
  .\Run-Project.ps1 doctor 3856
  .\Run-Project.ps1 validate-doctor
  .\Run-Project.ps1 tests
  .\Run-Project.ps1 benchmark-strict --baseline 40 --attack 80
  .\Run-Project.ps1 full-check -IncludeBenchmarks
"@ | Write-Host
}

function Invoke-ProjectTests {
    if (Test-PytestAvailable) {
        Invoke-PytestTests -Arguments $ScriptArgs
        return
    }

    Write-Status "pytest is not installed in the selected interpreter; falling back to unittest suites."
    Invoke-UnittestSuite -Pattern "test_raw_prompt_doctor.py"
    Invoke-UnittestSuite -Pattern "test_execution_harness.py"
}

function Invoke-FullCheck {
    Invoke-PythonScript -RelativePath "validate_doctor.py"
    Invoke-UnittestSuite -Pattern "test_raw_prompt_doctor.py"
    Invoke-UnittestSuite -Pattern "test_execution_harness.py"

    if (Test-PytestAvailable) {
        Invoke-PytestTests
    }
    else {
        Write-Status "Skipping pytest-only tests because pytest is not installed in the selected interpreter."
    }

    if ($IncludeBenchmarks) {
        Invoke-PythonScript -RelativePath "doctor_attack_benchmark_strict.py"
    }
}

$script:python = Get-PythonInterpreter
Write-Status "Using interpreter: $script:python"

switch ($Task) {
    "help" {
        Show-Help
    }
    "suggest" {
        Invoke-PythonScript -RelativePath "leetcode-tools\leetcode_suggestor.py" -Arguments $ScriptArgs
    }
    "doctor" {
        Invoke-PythonScript -RelativePath "leetcode-tools\leetcode_doctor.py" -Arguments $ScriptArgs
    }
    "main" {
        Invoke-PythonScript -RelativePath "main.py" -Arguments $ScriptArgs
    }
    "validate-doctor" {
        Invoke-PythonScript -RelativePath "validate_doctor.py"
    }
    "doctor-tests" {
        Invoke-UnittestSuite -Pattern "test_raw_prompt_doctor.py"
    }
    "execution-tests" {
        Invoke-UnittestSuite -Pattern "test_execution_harness.py"
    }
    "tests" {
        Invoke-ProjectTests
    }
    "doctor-grading" {
        Invoke-PythonScript -RelativePath "test_doctor_grading.py" -Arguments $ScriptArgs
    }
    "doctor-hardening" {
        Invoke-PythonScript -RelativePath "test_doctor_hardening.py" -Arguments $ScriptArgs
    }
    "benchmark" {
        Invoke-PythonScript -RelativePath "doctor_attack_benchmark.py" -Arguments $ScriptArgs
    }
    "benchmark-strict" {
        Invoke-PythonScript -RelativePath "doctor_attack_benchmark_strict.py" -Arguments $ScriptArgs
    }
    "benchmark-runner" {
        Invoke-PythonScript -RelativePath "benchmark_runner.py" -Arguments $ScriptArgs
    }
    "falsify" {
        Invoke-PythonScript -RelativePath "final_falsification_test.py" -Arguments $ScriptArgs
    }
    "full-check" {
        Invoke-FullCheck
    }
}

exit 0
