# Instructions for Desktop (PC B)

**Goal**: Upload the unique work from this computer (Desktop) to GitHub so it can be merged with the Laptop (PC A).

## Step 1: Open Terminal

Open your terminal (PowerShell or Command Prompt) and navigate to the project folder:
`d:\sandbox\smarketer-pro`

## Step 2: Create a Safety Branch

We want to isolate your work here before pushing. Run this command:

```powershell
git checkout -b feature/pc-b-work
```

## Step 3: Stage and Commit Changes

Capture all your current progress.

```powershell
git add .
git commit -m "Updates from Desktop (PC B)"
```

## Step 4: Push to GitHub

Send your branch to the cloud.

```powershell
git push -u origin feature/pc-b-work
```

## Step 5: Done

Once the push is successful, you are done on this computer. Return to your Laptop (PC A) and tell the Agent "PC B is pushed".
