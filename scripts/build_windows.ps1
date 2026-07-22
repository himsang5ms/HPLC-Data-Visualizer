param(
    [string]$Version = "1.3.0"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$Spec = Join-Path $RepoRoot "HPLC-Data-Visualizer.spec"
$DistDir = Join-Path $RepoRoot "dist"
$BundleDir = Join-Path $DistDir "HPLC Data Visualizer"
$ZipPath = Join-Path $DistDir "HPLC-Data-Visualizer-v$Version-Windows-x64.zip"

if (-not (Test-Path $Python)) {
    throw "Virtual environment not found at $Python"
}

Push-Location $RepoRoot
try {
    & $Python -m PyInstaller --noconfirm --clean $Spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed with exit code $LASTEXITCODE"
    }

    $QuickGuideZh = Join-Path $RepoRoot "output\pdf\HPLC-Data-Visualizer-v$Version-Quick-Guide-ZH.pdf"
    $QuickGuideEn = Join-Path $RepoRoot "output\pdf\HPLC-Data-Visualizer-v$Version-Quick-Guide-EN.pdf"
    Copy-Item -LiteralPath (Join-Path $RepoRoot "README.md") -Destination $BundleDir -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot "README_ZH.md") -Destination $BundleDir -Force
    Copy-Item -LiteralPath $QuickGuideZh -Destination $BundleDir -Force
    Copy-Item -LiteralPath $QuickGuideEn -Destination $BundleDir -Force

    if (Test-Path $ZipPath) {
        Remove-Item -LiteralPath $ZipPath -Force
    }

    Compress-Archive -Path $BundleDir -DestinationPath $ZipPath -CompressionLevel Optimal
    Write-Host "Portable bundle created: $ZipPath"
}
finally {
    Pop-Location
}
