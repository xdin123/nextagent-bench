param([switch]$SkipImport, [string]$Framework, [string]$Dataset)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { python -m venv .venv }
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12+ is required.' }
    & '.\.venv\Scripts\python.exe' -m pip install --disable-pip-version-check -e .
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    & '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Contract tests failed.' }
    if (-not $SkipImport) {
        $options = @('prepare', '--pin-defaults')
        if ($Framework) { $options += @('--framework', $Framework) }
        if ($Dataset) { $options += @('--dataset', $Dataset) }
        & '.\.venv\Scripts\python.exe' -m nextagent_bench @options
        if ($LASTEXITCODE -ne 0) { throw 'Artifact/dataset import failed.' }
    }
    Write-Output 'Setup complete. Set a model credential once, then use Start-Evaluation.ps1.'
} finally { Pop-Location }
