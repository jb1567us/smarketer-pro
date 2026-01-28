# Implementation Plan - Direct Search Scraper

The user has confirmed that manual searching ("Direct Method") yields excellent results where the complex proxy system failed. We will implement a script that automates this exact "human" behavior.

## Goal

Create a standalone tool `src/direct_scraper.py` that opens a real browser, performs a Google search, and extracts results, completely bypassing the `ProxyAgent`, `SearXNG`, and `Tor` infrastructure.

## User Review Required
>
> [!IMPORTANT]
> **Headless vs Headed Mode:** This tool will default to running in **Headed Mode** (you will see the browser open). This is safer for avoiding blocks.
> **Speed:** This will be slower than the proxy method (approx. 1 page per 10-20 seconds) to mimic human speed.

## Proposed Changes

### [B2B Outreach Tool Workspace](C:\sandbox\b2b_outreach_tool)

#### [NEW] [src/direct_scraper.py](file:///C:/sandbox/b2b_outreach_tool/src/direct_scraper.py)

A new standalone script using `playwright`.

- **Function:** `run_direct_search(query, num_pages=1)`
- **Logic:**
    1. Launches Playwright (Chromium).
    2. Navigates to Google.com.
    3. Types the query with random keystroke delays.
    4. Extracts result URLs.
    5. Clicks "Next" and repeats.
    6. Saves results to `direct_results.json` and a CSV.

#### [NEW] [run_direct_search.bat](file:///C:/sandbox/b2b_outreach_tool/run_direct_search.bat)

- A simple batch file to run the script for the user.

## Verification Plan

### Manual Verification

1. Run `run_direct_search.bat`.
2. Input the query: `site:instagram.com +"fitness"`.
3. Watch the browser open, type the query, and collect results.
4. Verify `direct_results.csv` contains the high-quality links the user saw manually.
