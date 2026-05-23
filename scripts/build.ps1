param(
    [string]$Version = "dev",
    [switch]$SkipInstall,
    [switch]$NoBuild
)

$ErrorActionPreference = "Stop"

$AppName = "PyFlowDownloader"
$Root = Resolve-Path "$PSScriptRoot\.."
$ReleaseDir = Join-Path $Root "releases"
$ZipPath = Join-Path $ReleaseDir "$AppName-$Version-windows.zip"

Set-Location $Root

if (-not $SkipInstall) {
    python -m pip install --upgrade pip
    pip install -r requirements.txt
}

Remove-Item -Recurse -Force "build", "dist" -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
Remove-Item -Force $ZipPath -ErrorAction SilentlyContinue

if ($NoBuild) {
    "Build skipped. Script syntax and paths are valid."
    exit 0
}

pyinstaller --noconfirm "PyFlowDownloader.spec"

Compress-Archive -Path "dist\$AppName\*" -DestinationPath $ZipPath -Force

"Release package created: $ZipPath"
