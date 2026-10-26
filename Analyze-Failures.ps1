param([string]$Run, [switch]$EvidenceOnly, [switch]$Background)
. (Join-Path $PSScriptRoot 'scripts\Common.ps1')
$options = @('analyze')
if ($Run) { $options += $Run }
if ($EvidenceOnly) { $options += '--evidence-only' }
Invoke-Bench -Arguments $options -Background:$Background -NeedsCredential:(-not $EvidenceOnly)
