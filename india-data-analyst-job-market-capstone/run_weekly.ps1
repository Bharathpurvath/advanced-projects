$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Project
python src/collect.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python src/analyze.py
exit $LASTEXITCODE
