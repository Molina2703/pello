[CmdletBinding()]
param(
    [string]$PythonExe = '',
    [switch]$RunSdkSmoke,
    [switch]$SkipAuthenticationCheck
)
$ErrorActionPreference = 'Stop'
$env:PIP_DISABLE_PIP_VERSION_CHECK = '1'
$env:PIP_NO_INPUT = '1'
$projectRoot = $PSScriptRoot
Set-Location -LiteralPath $projectRoot
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'evidence') | Out-Null
$setupLog = Join-Path $projectRoot ('evidence\setup-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log')

function Invoke-Checked {
    param([string]$Executable, [string[]]$ArgumentList)
    # Windows PowerShell 5.1 wraps native stderr (including pip notices) in
    # ErrorRecord objects. Decide failure from the actual process exit code.
    $ErrorActionPreference = 'Continue'
    & $Executable @ArgumentList 2>&1 | Tee-Object -FilePath $setupLog -Append | Write-Host
    if ($LASTEXITCODE -ne 0) { throw "Command failed (exit $LASTEXITCODE): $Executable" }
}
function Refresh-UserPath {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
}
function Find-Python {
    $ErrorActionPreference = 'Continue'
    $pythonCandidates = @()
    if ($PythonExe) { $pythonCandidates += $PythonExe }
    $pythonCandidates += (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe')
    foreach ($name in @('python.exe', 'python3.exe')) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) { $pythonCandidates += $command.Source }
    }
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        $resolved = & $launcher.Source -3 -c 'import sys; print(sys.executable)' 2>$null
        if ($LASTEXITCODE -eq 0) { $pythonCandidates += [string]$resolved }
    }
    foreach ($candidate in $pythonCandidates) {
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { continue }
        & $candidate -c 'import sys, venv; raise SystemExit(0 if sys.version_info >= (3,10) and sys.maxsize > 2**32 else 1)' 2>$null
        if ($LASTEXITCODE -eq 0) { return $candidate }
    }
    return $null
}
function Install-UserPrerequisite {
    param([string]$PackageId)
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) { throw "Cannot automatically install ${PackageId}: WinGet unavailable. Install this prerequisite and rerun setup." }
    Invoke-Checked -Executable $winget.Source -ArgumentList @('install', '--id', $PackageId, '--exact', '--source', 'winget', '--scope', 'user', '--silent', '--accept-package-agreements', '--accept-source-agreements', '--disable-interactivity')
    Refresh-UserPath
}

try {
    if ($env:OS -ne 'Windows_NT') { throw 'Use this script on Windows. See INSTALL.md for other systems.' }
    $python = Find-Python
    if (-not $python) {
        Install-UserPrerequisite -PackageId 'Python.Python.3.12'
        $python = Find-Python
    }
    if (-not $python) { throw 'A working 64-bit Python 3.10+ could not be found. Use -PythonExe with its full path.' }
    if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { Install-UserPrerequisite -PackageId 'Git.Git' }
    if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { throw 'Git unavailable after installation; reopen PowerShell and rerun setup.' }
    $venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $venvPython)) {
        Invoke-Checked -Executable $python -ArgumentList @('-m', 'venv', (Join-Path $projectRoot '.venv'))
    }
    Invoke-Checked -Executable $venvPython -ArgumentList @('-c', 'import sys; assert sys.prefix != sys.base_prefix; assert sys.version_info >= (3,10); print(sys.version); print(sys.executable)')
    Invoke-Checked -Executable $venvPython -ArgumentList @('-m', 'pip', 'install', '-r', (Join-Path $projectRoot 'requirements-lock.txt'))
    Invoke-Checked -Executable $venvPython -ArgumentList @('-m', 'pip', 'install', '--no-deps', '-e', $projectRoot)
    Invoke-Checked -Executable $venvPython -ArgumentList @('-m', 'athis_autopilot.installation', '--init')
    Invoke-Checked -Executable $venvPython -ArgumentList @('-m', 'athis_autopilot.installation', '--verify')
    if (-not $SkipAuthenticationCheck) {
        & $venvPython -m athis_autopilot doctor --check-auth | Tee-Object -FilePath $setupLog -Append | Write-Host
        if ($LASTEXITCODE -ne 0) {
            Write-Warning 'Local installation verified; Codex authentication is BLOCKED. Run .\pello.cmd login and complete the browser flow.'
            exit 2
        }
    }
    if ($RunSdkSmoke) {
        Invoke-Checked -Executable $venvPython -ArgumentList @('-m', 'athis_autopilot.sdk_smoke')
    }
    Write-Host 'Local installation and entry points verified. Use .\pello.cmd doctor. SDK model execution is verified only when a smoke result says REAL INTEGRATION VERIFIED.'
    exit 0
} catch {
    Write-Host ('SETUP FAILED: ' + $_.Exception.Message)
    Write-Host ('Log: ' + $setupLog)
    exit 1
}
