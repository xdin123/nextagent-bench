$ErrorActionPreference = 'Stop'
$BenchProject = Split-Path -Parent $PSScriptRoot
$BenchPython = Join-Path $BenchProject '.venv\Scripts\python.exe'

function Read-BenchSecret {
    param([string]$Path)
    $secureValue = Import-Clixml -LiteralPath $Path
    $buffer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureValue)
    try { [Runtime.InteropServices.Marshal]::PtrToStringBSTR($buffer) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($buffer) }
}

function Get-BenchKeyRing {
    if ($env:NAB_API_KEYS) { return $env:NAB_API_KEYS }
    $entries = [Collections.Generic.List[object]]::new()
    $values = [Collections.Generic.HashSet[string]]::new()
    if ($env:OPENAI_API_KEY) {
        $entries.Add(@{name='environment'; key=$env:OPENAI_API_KEY})
        $values.Add($env:OPENAI_API_KEY) | Out-Null
    }
    $keyDirectory = Join-Path $BenchProject '.secrets\keys'
    if (Test-Path -LiteralPath $keyDirectory) {
        foreach ($file in Get-ChildItem -LiteralPath $keyDirectory -Filter '*.xml' | Sort-Object Name) {
            $value = Read-BenchSecret -Path $file.FullName
            if ($values.Add($value)) { $entries.Add(@{name=$file.BaseName; key=$value}) }
        }
    }
    $legacy = Join-Path $BenchProject '.secrets\openai-api-key.xml'
    if ((Test-Path -LiteralPath $legacy) -and -not (Test-Path -LiteralPath (Join-Path $keyDirectory 'default.xml'))) {
        $value = Read-BenchSecret -Path $legacy
        if ($values.Add($value)) { $entries.Add(@{name='legacy-default'; key=$value}) }
    }
    if ($entries.Count -eq 0) { throw 'Run .\Set-ModelCredential.ps1 -Name default once, or set OPENAI_API_KEY.' }
    ConvertTo-Json -InputObject @($entries.ToArray()) -Compress
}

function Invoke-Bench {
    param([string[]]$Arguments, [switch]$Background, [switch]$NeedsCredential)
    if (-not (Test-Path -LiteralPath $BenchPython)) { throw 'Run .\Setup.ps1 once first.' }
    $savedKeyRing = $env:NAB_API_KEYS
    if ($NeedsCredential) { $env:NAB_API_KEYS = Get-BenchKeyRing }
    try {
    if ($Background) {
        $launchPath = Join-Path $BenchProject 'launches'
        New-Item -ItemType Directory -Path $launchPath -Force | Out-Null
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-ffff'
        $outputPath = Join-Path $launchPath ($stamp + '.stdout.log')
        $errorPath = Join-Path $launchPath ($stamp + '.stderr.log')
        $quoted = @('-m', 'nextagent_bench') + $Arguments | ForEach-Object { '"' + $_.Replace('"', '\"') + '"' }
        $process = Start-Process -FilePath $BenchPython -ArgumentList $quoted -WorkingDirectory $BenchProject -WindowStyle Hidden -PassThru -RedirectStandardOutput $outputPath -RedirectStandardError $errorPath
        Write-Output "Runner PID: $($process.Id)"
        Write-Output "Progress: $outputPath"
        Write-Output "Errors: $errorPath"
    } else {
        Push-Location $BenchProject
        try {
            & $BenchPython -m nextagent_bench @Arguments
            if ($LASTEXITCODE -ne 0) { throw "Evaluator exited with code $LASTEXITCODE" }
        } finally { Pop-Location }
    }
    } finally {
        if ($null -eq $savedKeyRing) { Remove-Item Env:\NAB_API_KEYS -ErrorAction SilentlyContinue }
        else { $env:NAB_API_KEYS = $savedKeyRing }
    }
}
