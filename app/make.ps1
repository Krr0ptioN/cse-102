[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Task = "help",
    [switch]$NoReset
)

$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ScriptDir)) {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}

$script:PythonLauncher = ""

function Show-Usage {
    Write-Host "Usage: .\make.ps1 <task> [-NoReset]"
    Write-Host ""
    Write-Host "Tasks:"
    Write-Host "  setup         Create .venv and install runtime dependencies"
    Write-Host "  install-dev   Install runtime + dev dependencies"
    Write-Host "  install-build Install runtime + build dependencies"
    Write-Host "  run           Launch the Tkinter app"
    Write-Host "  test          Run pytest"
    Write-Host "  db-setup      Initialize database schema"
    Write-Host "  seed          Seed mock data (resets DB by default)"
    Write-Host "  db-status     Print row counts for all tables"
    Write-Host "  compile       Build standalone binary with PyInstaller"
    Write-Host "  clean         Remove .venv and __pycache__ directories"
    Write-Host "  help          Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\make.ps1 setup"
    Write-Host "  .\make.ps1 run"
    Write-Host "  .\make.ps1 seed -NoReset"
    Write-Host "  .\make.ps1 compile"
}

function Resolve-PythonLauncher {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return "py"
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return "python"
    }
    throw "Python 3.11+ is required but was not found in PATH."
}

function Assert-Python {
    $script:PythonLauncher = Resolve-PythonLauncher
    & $script:PythonLauncher --version
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to execute Python launcher '$script:PythonLauncher'."
    }
}

function Get-VenvPython {
    if ($env:OS -eq "Windows_NT") {
        return Join-Path $ScriptDir ".venv\Scripts\python.exe"
    }
    return Join-Path $ScriptDir ".venv/bin/python"
}

function Invoke-Strict {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Executable,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

function Assert-Venv {
    $venvPython = Get-VenvPython
    if (-not (Test-Path $venvPython)) {
        throw "Virtual environment not found. Run '.\make.ps1 setup' first."
    }
    return $venvPython
}

function Invoke-InVenv {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$CommandArgs
    )

    $venvPython = Assert-Venv
    $previousPythonPath = $env:PYTHONPATH
    $env:PYTHONPATH = ".."
    try {
        Invoke-Strict -Executable $venvPython -Arguments $CommandArgs
    }
    finally {
        if ($null -eq $previousPythonPath) {
            Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
        }
        else {
            $env:PYTHONPATH = $previousPythonPath
        }
    }
}

function Install-Dependencies {
    param(
        [switch]$IncludeDev,
        [switch]$IncludeBuild
    )

    Invoke-Strict -Executable $script:PythonLauncher -Arguments @("-m", "venv", ".venv")
    $venvPython = Get-VenvPython

    Invoke-Strict -Executable $venvPython -Arguments @(
        "-m", "pip", "install", "-r", "requirements.txt"
    )

    if ($IncludeDev) {
        Invoke-Strict -Executable $venvPython -Arguments @(
            "-m", "pip", "install", "-r", "requirements-dev.txt"
        )
    }

    if ($IncludeBuild) {
        Invoke-Strict -Executable $venvPython -Arguments @(
            "-m", "pip", "install", "-r", "requirements-build.txt"
        )
    }
}

function Ensure-BuildDependencies {
    if (-not (Test-Path (Get-VenvPython))) {
        Install-Dependencies -IncludeBuild
        return
    }

    $venvPython = Get-VenvPython
    Invoke-Strict -Executable $venvPython -Arguments @(
        "-m", "pip", "install", "-r", "requirements-build.txt"
    )
}

function Clean-Workspace {
    $venvPath = Join-Path $ScriptDir ".venv"
    if (Test-Path $venvPath) {
        Remove-Item $venvPath -Recurse -Force
    }

    Get-ChildItem -Path $ScriptDir -Filter "__pycache__" -Directory -Recurse -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-Item $_.FullName -Recurse -Force }
}

Push-Location $ScriptDir
try {
    Assert-Python

    switch ($Task.ToLowerInvariant()) {
        "setup" {
            Install-Dependencies
            break
        }
        "install-dev" {
            Install-Dependencies -IncludeDev
            break
        }
        "install-build" {
            Install-Dependencies -IncludeBuild
            break
        }
        "run" {
            Invoke-InVenv -CommandArgs @("-m", "app.main")
            break
        }
        "test" {
            Invoke-InVenv -CommandArgs @("-m", "pytest")
            break
        }
        "db-setup" {
            Invoke-InVenv -CommandArgs @("scripts/init_db.py")
            break
        }
        "seed" {
            $seedArgs = @("scripts/seed_mock_data.py")
            if (-not $NoReset) {
                $seedArgs += "--reset"
            }
            Invoke-InVenv -CommandArgs $seedArgs
            break
        }
        "db-status" {
            Invoke-InVenv -CommandArgs @("scripts/db_status.py")
            break
        }
        "compile" {
            Ensure-BuildDependencies
            Invoke-InVenv -CommandArgs @("scripts/build_release.py", "--clean")
            break
        }
        "clean" {
            Clean-Workspace
            break
        }
        "help" {
            Show-Usage
            break
        }
        default {
            Write-Error "Unknown task '$Task'."
            Show-Usage
            exit 1
        }
    }
}
finally {
    Pop-Location
}
