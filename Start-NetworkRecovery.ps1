param([Parameter(Mandatory=$true)][string]$Run)
. (Join-Path $PSScriptRoot 'scripts\Common.ps1')
$runDirectory = if (Test-Path -LiteralPath $Run -PathType Container) { (Resolve-Path -LiteralPath $Run).Path } else { Join-Path $PSScriptRoot ('runs\' + $Run) }
if (-not (Test-Path -LiteralPath (Join-Path $runDirectory 'network-retry-plan.json'))) { throw 'Network retry plan is missing.' }
$retryPlan = Get-Content -LiteralPath (Join-Path $runDirectory 'network-retry-plan.json') -Raw | ConvertFrom-Json
if ($retryPlan.status -eq 'CANCELLED_BY_USER_PENDING_RETRY_APPROVAL') { throw 'The user cancelled this retry plan. Fresh user approval is required.' }
$savedKeys = $env:NAB_API_KEYS
try {
    $env:NAB_API_KEYS = Get-BenchKeyRing
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-ffff'
    $stdout = Join-Path $PSScriptRoot ('launches\' + $stamp + '-network-recovery.stdout.log')
    $stderr = Join-Path $PSScriptRoot ('launches\' + $stamp + '-network-recovery.stderr.log')
    $arguments = @(('"' + (Join-Path $PSScriptRoot 'scripts\prepare_network_recovery.py') + '"'), ('"' + $runDirectory + '"'))
    $process = Start-Process -FilePath $BenchPython -ArgumentList $arguments -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    Write-Output "Network recovery launcher PID: $($process.Id)"
    Write-Output "Progress: $stdout"
    Write-Output "Errors: $stderr"
} finally {
    if ($null -eq $savedKeys) { Remove-Item Env:\NAB_API_KEYS -ErrorAction SilentlyContinue }
    else { $env:NAB_API_KEYS=$savedKeys }
}
