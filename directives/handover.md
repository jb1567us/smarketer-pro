# Directive: Handover (Save & Report)

**Goal**: Store the data and notify the user.
**Priority**: Data Integrity.

## Strategy

1. **Format Data**: Ensure all fields (Company, URL, Email, Confidence) are standardized.
2. **Save Local**:
    - Append to `leads.csv` (Master list).
    - Insert into SQLite `leads.db`.
3. **Notification (Optional)**:
    - If `notify_on_match` is True: Send a ping to Slack/Discord with the lead details.
    - "Found: [Company Name] - [Email] (Score: 95/100)"

## Inputs

- `lead_data`: JSON object of the final lead.
- `destination`: "csv", "db", "webhook".

## Execution Tool

- `orchestrator.py` (Handles writing to file).
