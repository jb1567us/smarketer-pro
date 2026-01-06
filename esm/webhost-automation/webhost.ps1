<#
.SYNOPSIS
Portable wrapper for Webhost Automation Tool.
Allows running the tool without global installation.

.EXAMPLE
.\webhost.ps1 status
.\webhost.ps1 files-list public_html
#>

$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
$Env:PYTHONPATH = "$ScriptDir;$Env:PYTHONPATH"

# Check if venv exists in this folder (preferred)
if (Test-Path "$ScriptDir\.venv\Scripts\python.exe") {
    & "$ScriptDir\.venv\Scripts\python.exe" -m webhost_automation.cli $args
} else {
    # Fallback to system python
    python -m webhost_automation.cli $args
}
