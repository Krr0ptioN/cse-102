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

function Show-Usage {
    Write-Host "Usage: .\make.ps1 <task> [-NoReset]"
    Write-Host ""
    Write-Host "Tasks:"
    Write-Host "  setup       Create .venv and install runtime dependencies"
    Write-Host "  install-dev Create .venv and install runtime + dev dependencies"
    Write-Host "  run         Launch the Tkinter app"
    Write-Host "  test        Run pytest"
    Write-Host "  db-setup    Initialize database schema"
    Write-Host "  seed        Seed mock data (resets DB by default)"
    Write-Host "  db-status   Print row counts for all tables"
    Write-Host "  clean       Remove .venv and __pycache__ directories"
    Write-Host "  help        Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\make.ps1 setup"
    Write-Host "  .\make.ps1 run"
    Write-Host "  .\make.ps1 seed -NoReset"
}

function Assert-Uv {
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        throw "uv is required but was not found in PATH. Install it from https://docs.astral.sh/uv/."
    }
}

function Get-VenvPython {
    if ($env:OS -eq "Windows_NT") {
        return Join-Path $ScriptDir ".venv\Scripts\python.exe"
    }
    return Join-Path $ScriptDir ".venv/bin/python"
}

function Invoke-Uv {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$UvArgs
    )

    & uv @UvArgs
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

function Invoke-AppCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$CommandArgs
    )

    $venvPython = Assert-Venv
    $previousPythonPath = $env:PYTHONPATH
    $env:PYTHONPATH = ".."
    try {
        $uvArgs = @("run", "--python", $venvPython) + $CommandArgs
        Invoke-Uv -UvArgs $uvArgs
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
    param([switch]$IncludeDev)

    Invoke-Uv -UvArgs @("venv", ".venv")
    $venvPython = Get-VenvPython
    Invoke-Uv -UvArgs @("pip", "install", "--python", $venvPython, "-r", "requirements.txt")

    if ($IncludeDev) {
        Invoke-Uv -UvArgs @("pip", "install", "--python", $venvPython, "-r", "requirements-dev.txt")
    }
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
    Assert-Uv

    switch ($Task.ToLowerInvariant()) {
        "setup" {
            Install-Dependencies
            break
        }
        "install-dev" {
            Install-Dependencies -IncludeDev
            break
        }
        "run" {
            Invoke-AppCommand -CommandArgs @("python", "-m", "app.main")
            break
        }
        "test" {
            Invoke-AppCommand -CommandArgs @("pytest")
            break
        }
        "db-setup" {
            Invoke-AppCommand -CommandArgs @("python", "scripts/init_db.py")
            break
        }
        "seed" {
            $seedArgs = @("python", "scripts/seed_mock_data.py")
            if (-not $NoReset) {
                $seedArgs += "--reset"
            }
            Invoke-AppCommand -CommandArgs $seedArgs
            break
        }
        "db-status" {
            Invoke-AppCommand -CommandArgs @("python", "scripts/db_status.py")
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
