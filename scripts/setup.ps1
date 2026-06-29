$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

py -3.14 -m pip install --requirement requirements.txt
py -3.14 -m pip install pre-commit
py -3.14 -m pre_commit install
