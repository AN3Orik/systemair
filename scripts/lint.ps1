$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

py -3.14 -m ruff format .
py -3.14 -m ruff check . --fix
