$backupDir = "c:\sandbox\b2b_outreach_tool\_cleanup_backup"
$sandboxDir = "c:\sandbox"
$nestedRepo = Join-Path $backupDir "b2b_outreach_tool"

# 1. Delete nested b2b_outreach_tool
if (Test-Path $nestedRepo) {
    Write-Host "Deleting nested repository copy: $nestedRepo"
    Remove-Item -Path $nestedRepo -Recurse -Force -ErrorAction SilentlyContinue
}
else {
    Write-Host "Nested repository copy not found."
}

# 2. Move remaining contents to c:\sandbox (parent)
$items = Get-ChildItem -Path $backupDir

foreach ($item in $items) {
    $dest = Join-Path $sandboxDir $item.Name
    Write-Host "Moving $($item.Name) to $dest"
    
    if (Test-Path $dest) {
        Write-Host "Destination exists. Merging/Overwriting..."
        # For directories, Move-Item can be finicky if dest exists. 
        # Using Robocopy logic or Force Move is safer if we want to merge? 
        # Actually, Move-Item -Force usually fails for existing dirs on some PS versions.
        # Let's try Move-Item first, if fails, manual move.
        
        try {
            Move-Item -Path $item.FullName -Destination $sandboxDir -Force -ErrorAction Stop
        }
        catch {
            Write-Host "Move failed (likely exists). Attempting recursive copy/delete..."
            if ($item.PSIsContainer) {
                # Copy content
                Copy-Item -Path "$($item.FullName)\*" -Destination $dest -Recurse -Force
                Remove-Item -Path $item.FullName -Recurse -Force
            }
            else {
                Copy-Item -Path $item.FullName -Destination $dest -Force
                Remove-Item -Path $item.FullName -Force
            }
        }
    }
    else {
        Move-Item -Path $item.FullName -Destination $sandboxDir -Force
    }
}

# 3. Remove backup dir if empty
if ((Get-ChildItem -Path $backupDir).Count -eq 0) {
    Write-Host "Removing empty backup directory."
    Remove-Item -Path $backupDir -Force
}

Write-Host "Finalization complete."
