# Find largest folders in AppData\Local

$localAppData = "$env:LOCALAPPDATA"

Write-Host "=== Top 25 Largest Folders in AppData\Local ==="
Write-Host ""

$items = Get-ChildItem -Path $localAppData -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $folder = $_
    $size = 0
    try {
        $size = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    } catch {}
    
    [PSCustomObject]@{
        Folder = $folder.Name
        Path = $folder.FullName
        SizeGB = [math]::Round($size, 2)
    }
}

$items | Sort-Object SizeGB -Descending | Select-Object -First 25 | Format-Table -AutoSize
