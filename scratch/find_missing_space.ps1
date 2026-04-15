# Check other large space consumers

Write-Host "=== Windows Folder ==="
$winSize = (Get-ChildItem "C:\Windows" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
Write-Host "C:\Windows : $([math]::Round($winSize, 2)) GB"

Write-Host ""
Write-Host "=== Pagefile ==="
$pf = Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" -Name PagingFiles -ErrorAction SilentlyContinue
if ($pf) { Write-Host "Pagefile: $($pf.PagingFiles)" }

Write-Host ""
Write-Host "=== Hiberfil.sys ==="
$hiber = Get-Item "C:\hiberfil.sys" -ErrorAction SilentlyContinue
if ($hiber) { 
    $hiberSize = $hiber.Length / 1GB
    Write-Host "Hiberfil.sys : $([math]::Round($hiberSize, 2)) GB"
}

Write-Host ""
Write-Host "=== System Restore ==="
$srPath = "C:\System Volume Information"
if (Test-Path $srPath) {
    try {
        $srSize = (Get-ChildItem $srPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        Write-Host "System Volume Information : $([math]::Round($srSize, 2)) GB"
    } catch {
        Write-Host "Access denied to System Volume Information"
    }
}

Write-Host ""
Write-Host "=== Games ==="
$gamePaths = @(
    "C:\Program Files\Steam",
    "C:\Program Files (x86)\Steam",
    "C:\Games",
    "C:\Program Files\Epic Games",
    "C:\Program Files (x86)\Epic Games"
)

foreach ($path in $gamePaths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        Write-Host "$path : $([math]::Round($size, 2)) GB"
    }
}

Write-Host ""
Write-Host "=== OneDrive/Cloud Storage Local ==="
$onedrive = "$env:USERPROFILE\OneDrive"
if (Test-Path $onedrive) {
    $size = (Get-ChildItem $onedrive -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$onedrive : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== Downloads folder ==="
$downloads = "$env:USERPROFILE\Downloads"
if (Test-Path $downloads) {
    $size = (Get-ChildItem $downloads -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$downloads : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== Documents folder ==="
$docs = "$env:USERPROFILE\Documents"
if (Test-Path $docs) {
    $size = (Get-ChildItem $docs -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$docs : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== Hidden/Debug Logs ==="
$debugPath = "C:\$WINDOWS.~BT"
if (Test-Path $debugPath) {
    $size = (Get-ChildItem $debugPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$debugPath : $([math]::Round($size, 2)) GB"
}

$installPath = "C:\$INPLACE.~BT"
if (Test-Path $installPath) {
    $size = (Get-ChildItem $installPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$installPath : $([math]::Round($size, 2)) GB"
}
