# B2B Outreach Tool

Automated lead generation and outreach toolkit.

## Setup

1. **Install Python Dependencies:**

    ```powershell
    pip install -r requirements.txt
    ```

2. **Start Local Search Engine (SearXNG):**

    ```powershell
    cd searxng
    docker-compose up -d
    cd ..
    ```

3. **Configure SMTP (Optional for sending emails):**
    Set environment variables `SMTP_USER` and `SMTP_PASS`.

## Usage

Run the workflow to find leads:

```powershell
python src/workflow.py "your search query"
```

Example:

```powershell
python src/workflow.py "software agencies Austin"
```

## Structure

- `src/`: Python source code (scraper, extractor, workflow).
- `searxng/`: Docker configuration for local search engine.
