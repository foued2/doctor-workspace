# Break down ProgramData

Write-Host "=== ProgramData Breakdown (>0.1 GB) ==="
$pdPath = "C:\ProgramData"
Get-ChildItem $pdPath -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $folder = $_.FullName
    $size = (Get-ChildItem $folder -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    if ($size -gt 0.1) {
        Write-Host "$($_.Name).PadRight(35) : $([math]::Round($size, 2)) GB"
    }
}
