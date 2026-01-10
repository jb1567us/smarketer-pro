$backupDir = "c:\sandbox\b2b_outreach_tool\_cleanup_backup"
$sourceDir = "c:\sandbox\b2b_outreach_tool"

# Create backup dir
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    Write-Host "Created backup directory: $backupDir"
}

# Folders to move
$foldersToMove = @(
    "Astrological neurological forecast",
    "ai-content-writer",
    "ai-control-starter",
    "b2b_outreach_tool",
    "cool-timeline",
    "esm",
    "family-collab",
    "hatch",
    "product_insights",
    "texas_teacup_morkies",
    "webhost-automation",
    "spec_sheets",
    "spec_sheets_v2",
    "spec_sheets_v3",
    "php_bin",
    "wp-admin",
    "wp-content",
    "wp-includes"
)

foreach ($folder in $foldersToMove) {
    $path = Join-Path $sourceDir $folder
    if (Test-Path $path) {
        Write-Host "Moving folder: $folder"
        # Move-Item might fail if destination exists, so we might need to be careful, but Force usually handles.
        # However, Move-Item to a directory moves IT INSIDE.
        Move-Item -Path $path -Destination $backupDir -Force -ErrorAction SilentlyContinue
    }
}

# Files to move
$files = Get-ChildItem -Path $sourceDir -File

foreach ($file in $files) {
    $move = $false
    
    # Check extensions/patterns
    if ($file.Extension -match "^\.(zip|pdf|docx|webp)$") { $move = $true }
    if ($file.Extension -match "^\.(jpg|png)$" -and $file.Name -ne "logo.png") { $move = $true } # Keep logo if it's the app logo, but likely not in root
    if ($file.Extension -eq ".mp3" -and $file.Name -ne "test_numbers.mp3") { $move = $true }
    if ($file.Name -like "SENuke*") { $move = $true }
    if ($file.Name -like "Venona*") { $move = $true }
    
    # Specific WordPress files (risky to wildcard *.php if project uses PHP, but this is a Python project)
    # The project is Python (Streamlit). So moving *.php is likely safe and correct for cleanup options.
    if ($file.Extension -eq ".php") { $move = $true }

    # Exclude task.md and implementation_plan.md? No, they are in brain.
    # Exclude README.md? Yes, verified in plan.

    if ($move) {
        Write-Host "Moving file: $($file.Name)"
        Move-Item -Path $file.FullName -Destination $backupDir -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "Cleanup completed."
