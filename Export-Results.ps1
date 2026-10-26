param([string]$Run)
. (Join-Path $PSScriptRoot 'scripts\Common.ps1')
$options = @('report')
if ($Run) { $options += $Run }
Invoke-Bench -Arguments $options
