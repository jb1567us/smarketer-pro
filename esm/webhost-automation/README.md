# Webhost Automation Tool

A Python-based automation tool for shared hosting environments running cPanel (LAMP stack).
Supports both **UAPI** (direct API) and **Browser Automation** (Playwright).

## Features
- **Status Monitoring**: View domain list and disk usage alerts.
- **WordPress Management**: List instances, trigger updates (via WP Toolkit).
- **Backups**: Trigger full account backups (API or Browser).
- **Extensible**: modular design.

## Installation

### Prerequisites
- Python 3.9+ 
- A cPanel account.

### Setup

1.  **Clone/Download** this repository.
2.  **Install dependencies**:
    ```bash
    pip install .
    playwright install chromium
    ```

3.  **Configuration**:
    Create a `.env` file:
    ```ini
    CPANEL_URL="https://your-domain.com:2083"
    CPANEL_USER="your_username"
    # For API Mode:
    CPANEL_TOKEN="your_api_token"
    # For Browser Mode:
    CPANEL_PASSWORD="your_password"
    ```

## Usage

### standard API Mode (Fast, Headless)
```bash
python -m webhost_automation.cli status
python -m webhost_automation.cli wp-list
python -m webhost_automation.cli backup
```

### Browser Mode (Simulates User)
If the API is blocked or restricted, use the browser mode. This opens a real Chromium instance to perform tasks.

```bash
# Trigger Backup via Browser
python -m webhost_automation.cli backup-browser

# To see the browser window (screen visible), pass --no-headless (defaults to headless in code, logic might vary, usually --no-headless flag in Typer needs specific implementation or just --headless=False).
# In our CLI currently:
python -m webhost_automation.cli backup-browser --no-headless
```

## Troubleshooting
- **Playwright Errors**: Ensure you ran `playwright install chromium`.
- **Login fails**: Check `CPANEL_PASSWORD`.
