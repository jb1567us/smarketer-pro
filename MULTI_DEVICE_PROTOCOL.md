# Multi-Device Development Protocol

**Goal**: Seamlessly switch between Laptop (PC A) and Desktop (PC B) without losing work or creating conflicts.

## The Golden Rule: Sync Before & After

Treat GitHub as the "Cloud Save" for your code. You must upload your save before quitting, and download the save before starting on a new machine.

### 1. STARTING a Session (On ANY computer)

**Before you write a single line of code**, open your terminal and run:

```powershell
git pull origin main
```

*Why?* This ensures you have the latest work from the other computer.

### 2. ENDING a Session (On ANY computer)

**Before you walk away**, create a "Save Point":

```powershell
git add .
git commit -m "Progress update [Time/Date]"
git push origin main
```

*Why?* If you don't push, the code stays trapped on that computer's hard drive.

---

## Troubleshooting

### "I forgot to push from the other PC!"

*Scenario: You worked on the Laptop, forgot to push, and are now at the Desktop.*

**Option A (Safe)**: Go back to the Laptop and push.
**Option B (Risk)**: Work on *different* files on the Desktop.

* If you edit `file_A.py` on Laptop (unpushed) and then edit `file_A.py` on Desktop, you will have a **Conflict** later.
* If you work on a completely new file, you are usually safe.

### "Git says 'Merge Conflict' when I pull"

This means you edited the same file on both computers without syncing.

1. Don't panic.
2. Open the file in your code editor.
3. Look for `<<<<<<<` and `>>>>>>>` markers.
4. Delete the lines you don't want.
5. `git add .`, `git commit`, `git push`.
