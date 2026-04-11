$release = Invoke-RestMethod 'https://api.github.com/repos/BurntSushi/ripgrep/releases/latest'
$asset = $release.assets | Where-Object { $_.name -match 'x86_64-pc-windows-msvc.zip$' } | Select-Object -First 1

if (-not $asset) {
    throw 'Could not find a Windows x64 ripgrep release asset.'
}

$installRoot = Join-Path $env:LOCALAPPDATA 'Programs\ripgrep'
$tempZip = Join-Path $env:TEMP 'ripgrep-latest.zip'
$tempExtract = Join-Path $env:TEMP 'ripgrep-extract'

if (Test-Path $tempExtract) {
    Remove-Item $tempExtract -Recurse -Force
}

if (Test-Path $installRoot) {
    Remove-Item $installRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $installRoot | Out-Null
Invoke-WebRequest $asset.browser_download_url -OutFile $tempZip
Expand-Archive $tempZip -DestinationPath $tempExtract -Force

$rgExe = Get-ChildItem $tempExtract -Recurse -Filter 'rg.exe' | Select-Object -First 1 -ExpandProperty FullName
if (-not $rgExe) {
    throw 'rg.exe was not found after extracting the archive.'
}

$binDir = Join-Path $installRoot 'bin'
New-Item -ItemType Directory -Path $binDir | Out-Null
Copy-Item $rgExe -Destination (Join-Path $binDir 'rg.exe') -Force

$supportFiles = Get-ChildItem $tempExtract -Recurse -File | Where-Object {
    $_.Name -in @('CHANGELOG.md', 'COPYING', 'LICENSE-MIT', 'README.md', 'UNLICENSE')
}

foreach ($file in $supportFiles) {
    Copy-Item $file.FullName -Destination (Join-Path $installRoot $file.Name) -Force
}

Remove-Item $tempExtract -Recurse -Force
Remove-Item $tempZip -Force

Write-Host "Installed ripgrep to $binDir"
& (Join-Path $binDir 'rg.exe') --version
