param(
    [ValidatePattern('^[A-Za-z0-9_-]{1,64}$')][string]$Name = 'default',
    [switch]$FromEnvironment,
    [switch]$List,
    [switch]$Remove
)
$ErrorActionPreference = 'Stop'
$credentialDirectory = Join-Path $PSScriptRoot '.secrets\keys'
if ($List) {
    Get-ChildItem -LiteralPath $credentialDirectory -Filter '*.xml' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty BaseName
    exit 0
}
if ($Remove) {
    Remove-Item -LiteralPath (Join-Path $credentialDirectory ($Name + '.xml')) -ErrorAction Stop
    Write-Output "Removed credential alias: $Name"
    exit 0
}
if ($FromEnvironment) {
    if (-not $env:OPENAI_API_KEY) { throw 'OPENAI_API_KEY is not set.' }
    $secureValue = ConvertTo-SecureString -String $env:OPENAI_API_KEY -AsPlainText -Force
} else {
    $secureValue = Read-Host -Prompt 'Model API key (saved encrypted for this Windows user)' -AsSecureString
}
New-Item -ItemType Directory -Path $credentialDirectory -Force | Out-Null
$secureValue | Export-Clixml -LiteralPath (Join-Path $credentialDirectory ($Name + '.xml'))
if ($Name -eq 'default') { Remove-Item -LiteralPath (Join-Path $PSScriptRoot '.secrets\openai-api-key.xml') -ErrorAction SilentlyContinue }
Write-Output "Saved credential alias '$Name' using Windows user encryption. The value is not printed or included in results."
