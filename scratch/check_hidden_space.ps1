# Check for hidden space consumers

Write-Host "=== System Files ==="
$sysFiles = @("C:\hiberfil.sys", "C:\pagefile.sys", "C:\swapfile.sys")
foreach ($f in $sysFiles) {
    $item = Get-Item $f -ErrorAction SilentlyContinue
    if ($item) {
        Write-Host "$($item.Name).PadRight(20) : $([math]::Round($item.Length/1GB, 2)) GB"
    } else {
        Write-Host "$f : NOT FOUND"
    }
}

Write-Host ""
Write-Host "=== Recycle Bin ==="
$shell = New-Object -ComObject Shell.Application
$recycleBin = $shell.NameSpace(0x0a)
if ($recycleBin) {
    $items = $recycleBin.Items()
    $totalSize = 0
    foreach ($item in $items) {
        $totalSize += $item.Size
    }
    Write-Host "Recycle Bin items: $($items.Count), Size: $([math]::Round($totalSize/1GB, 2)) GB"
}

Write-Host ""
Write-Host "=== Ollama on C: (old location) ==="
$ollamaOld = "C:\Users\foued\.ollama\models"
if (Test-Path $ollamaOld) {
    $size = (Get-ChildItem $ollamaOld -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$ollamaOld : $([math]::Round($size, 2)) GB"
} else {
    Write-Host "Not found"
}

Write-Host ""
Write-Host "=== Visual Studio Cache ==="
$vsCache = "C:\Users\foued\AppData\Local\Microsoft\VisualStudio"
if (Test-Path $vsCache) {
    $size = (Get-ChildItem $vsCache -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$vsCache : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== NuGet Cache ==="
$nuget = "C:\Users\foued\.nuget\packages"
if (Test-Path $nuget) {
    $size = (Get-ChildItem $nuget -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$nuget : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== Cargo Cache ==="
$cargo = "C:\Users\foued\.cargo\registry\cache"
if (Test-Path $cargo) {
    $size = (Get-ChildItem $cargo -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$cargo : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== Docker ==="
$docker = "C:\ProgramData\docker"
if (Test-Path $docker) {
    $size = (Get-ChildItem $docker -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$docker : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== MSSQL / SQL Server ==="
$mssql = "C:\Program Files\Microsoft SQL Server"
if (Test-Path $mssql) {
    $size = (Get-ChildItem $mssql -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$mssql : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== Hyper-V / VMs ==="
$hyperV = "C:\ProgramData\Hyper-V"
if (Test-Path $hyperV) {
    $size = (Get-ChildItem $hyperV -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$hyperV : $([math]::Round($size, 2)) GB"
}

Write-Host ""
Write-Host "=== Unreal Engine ==="
$ue = "C:\Program Files\Epic Games"
if (Test-Path $ue) {
    $size = (Get-ChildItem $ue -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$ue : $([math]::Round($size, 2)) GB"
}
