# Full breakdown of C: drive

Write-Host "=== SUMMARY OF C: DRIVE ==="
Write-Host ""

# System files
$hiber = Get-Item "C:\hiberfil.sys" -ErrorAction SilentlyContinue
$pagefile = Get-Item "C:\pagefile.sys" -ErrorAction SilentlyContinue
$swap = Get-Item "C:\swapfile.sys" -ErrorAction SilentlyContinue

if ($hiber) { Write-Host "Hiberfil.sys  : $([math]::Round($hiber.Length/1GB, 2)) GB" }
if ($pagefile) { Write-Host "Pagefile.sys  : $([math]::Round($pagefile.Length/1GB, 2)) GB" }
if ($swap) { Write-Host "Swapfile.sys  : $([math]::Round($swap.Length/1GB, 2)) GB" }

Write-Host ""
Write-Host "=== Major Folders ==="

$folders = @(
    "C:\Program Files",
    "C:\Program Files (x86)",
    "C:\Windows",
    "C:\Users\foued\AppData\Local",
    "C:\Users\foued\AppData\Roaming",
    "C:\Users\foued\OneDrive",
    "C:\Users\foued\Downloads",
    "C:\Users\foued\Documents",
    "C:\ProgramData\Microsoft\Windows Defender",
    "C:\$WINDOWS.~BT",
    "C:\$INPLACE.~BT"
)

$total = 0
foreach ($folder in $folders) {
    if (Test-Path $folder) {
        $size = (Get-ChildItem $folder -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        $total += $size
        Write-Host "$($folder.PadRight(45)) : $([math]::Round($size, 2)) GB"
    }
}

Write-Host "-----------------------------------------------------------"
Write-Host "$('TOTAL'.PadRight(45)) : $([math]::Round($total, 2)) GB"
Write-Host ""
Write-Host "=== Drive Info ==="
$drive = Get-PSDrive C
Write-Host "Total Size: $([math]::Round($drive.Used/1GB + $drive.Free/1GB, 2)) GB"
Write-Host "Used:       $([math]::Round($drive.Used/1GB, 2)) GB"
Write-Host "Free:       $([math]::Round($drive.Free/1GB, 2)) GB"
