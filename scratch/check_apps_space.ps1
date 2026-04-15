# Check Windows apps and related folders

Write-Host "=== Installed Programs Size ==="
$programPaths = @(
    "C:\Program Files",
    "C:\Program Files (x86)",
    "$env:ProgramFiles",
    "${env:ProgramFiles(x86)}"
)

foreach ($path in $programPaths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        Write-Host "$path : $([math]::Round($size, 2)) GB"
    }
}

Write-Host ""
Write-Host "=== AppData Folders ==="
$appDataPaths = @(
    "$env:LOCALAPPDATA",
    "$env:APPDATA"
)

foreach ($path in $appDataPaths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        Write-Host "$path : $([math]::Round($size, 2)) GB"
    }
}

Write-Host ""
Write-Host "=== Windows Update Cache ==="
$updatePath = "C:\Windows\SoftwareDistribution\Download"
if (Test-Path $updatePath) {
    $size = (Get-ChildItem $updatePath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$updatePath : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== Defender Quarantine ==="
$defenderPath = "C:\ProgramData\Microsoft\Windows Defender"
if (Test-Path $defenderPath) {
    $size = (Get-ChildItem $defenderPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$defenderPath : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== Windows Temp ==="
$winTemp = "C:\Windows\Temp"
if (Test-Path $winTemp) {
    $size = (Get-ChildItem $winTemp -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$winTemp : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== System Restore Shadow Copies ==="
$vssadmin = vssadmin list shadowstorage 2>&1 | Out-String
Write-Host $vssadmin
