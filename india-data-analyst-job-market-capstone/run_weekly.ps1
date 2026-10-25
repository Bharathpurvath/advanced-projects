$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Project
python src/collect.py --pages 2 --results-per-page 50
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python src/analyze.py
exit $LASTEXITCODE
