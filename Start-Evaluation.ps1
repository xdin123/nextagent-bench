param(
    [string]$Framework,
    [string]$Dataset,
    [string]$Suite = 'full',
    [string[]]$Tasks,
    [ValidateRange(1,32)][int]$Jobs = 2,
    [switch]$Background
)
. (Join-Path $PSScriptRoot 'scripts\Common.ps1')
$options = @('run', '--suite', $Suite, '--jobs', [string]$Jobs)
if ($Framework) { $options += @('--framework', $Framework) }
if ($Dataset) { $options += @('--dataset', $Dataset) }
if ($Tasks) { $options += '--tasks'; $options += $Tasks }
Invoke-Bench -Arguments $options -Background:$Background -NeedsCredential
