param([Parameter(Mandatory=$true)][string]$Run, [switch]$RetryErrors, [switch]$Recover, [switch]$Background,
      [string[]]$RetryTasks, [string]$RetryReason)
. (Join-Path $PSScriptRoot 'scripts\Common.ps1')
$options = @('resume', $Run)
if ($RetryErrors) { $options += '--retry-errors' }
if ($RetryTasks) {
    if ($RetryErrors -or -not $RetryReason) { throw 'Precise retries require a reason and cannot be combined with RetryErrors.' }
    $options += @('--retry-tasks') + $RetryTasks + @('--retry-reason', $RetryReason)
}
if ($Recover) { $options += '--recover' }
Invoke-Bench -Arguments $options -Background:$Background -NeedsCredential
