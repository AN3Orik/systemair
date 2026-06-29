$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$configPath = Join-Path $repoRoot "config"
if (-not (Test-Path -LiteralPath $configPath -PathType Container)) {
    New-Item -ItemType Directory -Path $configPath | Out-Null
    py -3.14 -m homeassistant --config $configPath --script ensure_config
}

$customComponentsPath = Join-Path $repoRoot "custom_components"
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$env:PYTHONPATH;$customComponentsPath"
} else {
    $env:PYTHONPATH = $customComponentsPath
}

py -3.14 -m homeassistant --config $configPath --debug
