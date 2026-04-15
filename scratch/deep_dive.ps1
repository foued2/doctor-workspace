# Check JetBrains breakdown and other potential space hogs

Write-Host "=== JetBrains Breakdown ==="
$jbPath = "C:\Users\foued\AppData\Local\JetBrains"
if (Test-Path $jbPath) {
    Get-ChildItem $jbPath -Directory | ForEach-Object {
        $folder = $_.FullName
        $size = (Get-ChildItem $folder -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        Write-Host "$($_.Name).PadRight(30) : $([math]::Round($size, 2)) GB"
    }
}

Write-Host ""
Write-Host "=== Programs Breakdown ==="
$progPath = "C:\Users\foued\AppData\Local\Programs"
if (Test-Path $progPath) {
    Get-ChildItem $progPath -Directory | ForEach-Object {
        $folder = $_.FullName
        $size = (Get-ChildItem $folder -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        Write-Host "$($_.Name).PadRight(30) : $([math]::Round($size, 2)) GB"
    }
}

Write-Host ""
Write-Host "=== Microsoft Breakdown ==="
$msPath = "C:\Users\foued\AppData\Local\Microsoft"
if (Test-Path $msPath) {
    Get-ChildItem $msPath -Directory | ForEach-Object {
        $folder = $_.FullName
        $size = (Get-ChildItem $folder -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        if ($size -gt 0.1) {
            Write-Host "$($_.Name).PadRight(30) : $([math]::Round($size, 2)) GB"
        }
    }
}

Write-Host ""
Write-Host "=== Chrome Cache ==="
$chrome = "C:\Users\foued\AppData\Local\Google\Chrome\User Data"
if (Test-Path $chrome) {
    $size = (Get-ChildItem $chrome -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$chrome : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== Check for large hidden folders in C:\ ==="
Get-ChildItem "C:\" -Directory -Force -ErrorAction SilentlyContinue | ForEach-Object {
    $folder = $_.FullName
    $size = (Get-ChildItem $folder -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    if ($size -gt 0.5) {
        Write-Host "$($_.Name).PadRight(30) : $([math]::Round($size, 2)) GB"
    }
}
