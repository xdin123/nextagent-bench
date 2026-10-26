param([Parameter(Mandatory=$true)][string]$Run, [Parameter(Mandatory=$true)][ValidateRange(1,32)][int]$Jobs,
      [string]$Reason = 'Operator requested runtime concurrency change')
. (Join-Path $PSScriptRoot 'scripts\Common.ps1')
Invoke-Bench -Arguments @('concurrency', $Run, '--jobs', [string]$Jobs, '--reason', $Reason)
