param([switch]$SkipImport, [switch]$SkipTests, [string]$Framework, [string]$Dataset)
$ErrorActionPreference = 'Stop'
$setupArguments = @('setup')
if ($SkipImport) { $setupArguments += '--skip-import' }
if ($SkipTests) { $setupArguments += '--skip-tests' }
if ($Framework) { $setupArguments += @('--framework', $Framework) }
if ($Dataset) { $setupArguments += @('--dataset', $Dataset) }
& python (Join-Path $PSScriptRoot 'bench.py') @setupArguments
if ($LASTEXITCODE -ne 0) { throw 'Setup failed. Python 3.12+ is required; see docs/ENVIRONMENT.md.' }
