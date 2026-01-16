import sys
import os
import asyncio
import csv
import time
import aiohttp
import functools

# Appends src and project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from dotenv import load_dotenv
load_dotenv()
from config import config
from utils.validator import ModelValidator
import os
from mailer import Mailer, get_email_content
from database import init_db, add_lead, mark_contacted
from analyzer import analyze_content

# === AGENT IMPORTS ===
from agents import ResearcherAgent, QualifierAgent
from enrichment_manager import EnrichmentManager

async def run_outreach(keywords, profile_names=["default"], target_niche=None, status_callback=None, exclusions=None, icp_criteria=None, max_results=None, auto_enrich=False):
    def log(msg):
        print(msg)
        if status_callback:
            status_callback(msg)

    # Handle single string input
    if isinstance(profile_names, str):
        profile_names = [profile_names]

    print("🚀 Starting Agentic Outreach Workflow (Smart Router v2)")
    
    # Run Pre-flight Checks
    ModelValidator.run_checks()

    log(f"Target: {keywords} | Niche: {target_niche}")
    
    init_db()
    
    # Initialize Proxies
    from proxy_manager import proxy_manager
    await proxy_manager.ensure_fresh_proxies()
    
    # Instantiate Agents
    researcher = ResearcherAgent()
    qualifier = QualifierAgent()
    
    async with aiohttp.ClientSession() as session:
        
        # === PHASE 1: DISCOVERY (Research Agent) ===
        log("\n--- Phase 1: Discovery (Researcher Agent) ---")
        
        # 1. Search (using Researcher)
        log("  [Agent] Researcher is searching...")
        search_context = {"query": keywords, "limit": max_results}
        search_result = await researcher.gather_intel(search_context)
        
        urls = search_result.get("results", [])
        
        if not urls:
            log("No results found.")
            return

        # 2. Filter Exclusions (Still useful to keep strict filters outside of LLM to save tokens)
        if exclusions:
             urls = [
                 u for u in urls 
                 if not any(ex.lower() in (u.get('url', '') if isinstance(u, dict) else u).lower() for ex in exclusions)
             ]
        
        log(f"Found {len(urls)} candidates.")
        
        if not urls: return

        # 3. Deep Analysis (Researcher + Qualifier Loop)
        # log(f"Analyzing {len(urls)} sites concurrently...") # Original line
        
        candidates = []
        
        # Throttling
        # Concurrency limit from config (Default: 20)
        limit = config.get("search", {}).get("concurrency", 20)
        log(f"Analyzing {len(urls)} candidates (Queue Size)...") # Updated to use len(urls) as candidates is empty
        log(f"  [System] Concurrency Throttle: {config['search']['concurrency']} parallel tasks")
        sem = asyncio.Semaphore(limit)

        # Debug Stats
        source_counts = {"organic": 0, "listing": 0}
        for u in urls:
            st = u.get("source_type", "organic") if isinstance(u, dict) else "organic"
            source_counts[st] = source_counts.get(st, 0) + 1
        log(f"  [Debug] Candidates Source Breakdown: {source_counts}")

        async def process_candidate(candidate):
            async with sem:
                # Handle legacy string format just in case, but prefer dict
                if isinstance(candidate, str):
                    url = candidate
                    source_type = "organic"
                else:
                    url = candidate.get("url")
                    source_type = candidate.get("source_type", "organic")

                log(f"  > Processing {url} ({source_type})...")

                # FILTER: Organic Filter Reworked
                # Allowing Organic results to pass through to the "Strict Email Check".
                # This ensures we don't drop direct business sites, but still skip junk (no email).
                # if source_type == "organic":
                #      log(f"    ⏭️ Skipping {url} (Organic result). Strict Filter Active.")
                #      return None
                
                # A. Research (Gather Intel)
                # Researcher agent "deep scrape" capability
                intel = await researcher.gather_intel({"url": url})
                
                if not intel.get('html_preview'):
                    return None
                
                # B. Qualify (Gatekeeper)
                if icp_criteria:
                    log(f"    [Agent] Qualifier is evaluating {url} against ICP...")
                    
                    # Construct context for qualifier
                    q_context = f"Company URL: {url}\nIndustry: {target_niche}\nContent Preview: {intel.get('html_preview', '')[:3000]}\n\nICP Criteria:\n{icp_criteria}"
                    
                    try:
                        qualification = qualifier.think(q_context)
                    except Exception as e:
                        log(f"    ⚠️ Qualification failed for {url}: {e}")
                        qualification = {'qualified': True, 'score': 50, 'reason': 'Error during qualification, allowing as neutral.'}
                else:
                    # AUTO-QUALIFY MODE ENABLED (only if no criteria provided)
                    log(f"    [Agent] Auto-Qualifying {url} (No ICP criteria provided)...")
                    
                    qualification = {
                        'qualified': True,
                        'score': 100,
                        'reason': f'Auto-Qualified ({source_type} - No strict ICP)'
                    }
                
                # Parse result
                if qualification:
                    if not qualification.get('qualified'):
                        log(f"    ❌ Rejected: {qualification.get('reason')}")
                        return None
                    else:
                        log(f"    ✅ Qualified! Score: {qualification.get('score')}")
                        
                        # Extract Details
                        # OPTIMIZATION: Strict Email Requirement
                        details = {}
                        has_emails = bool(intel.get('emails'))
                        
                        if has_emails:
                             log(f"    ⚡ Emails found ({len(intel.get('emails'))}). FAST SAVE.")
                             details = {
                                 "company_name": "Unknown (Fast Save)", 
                                 "confidence": 0.9
                             }
                        else:
                            # Only use LLM if we desperately need to find contact info
                            # With 90+ free models, we can afford this now!
                            try:
                                loop = asyncio.get_running_loop()
                                details = await loop.run_in_executor(
                                    None, 
                                    analyze_content, 
                                    url, 
                                    intel.get('html_preview'), 
                                    target_niche
                                )
                            except Exception as e:
                                log(f"    ⚠️ Details Extraction Failed for {url}: {e}")
                            # Proceed without details
                        
                        return {
                            "url": url,
                            "emails": intel.get('emails'),
                            "analysis": qualification,
                            "intel": intel,
                            "details": details or {}
                        }
                return None

        tasks = [process_candidate(u) for u in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results and log errors
        candidates = []
        for r in results:
            if isinstance(r, Exception):
                log(f"    ⚠️ Task failed: {r}")
            elif r:
                candidates.append(r)
        
        log(f"Phase 2 Complete. {len(candidates)} qualified leads found.")

    # === PHASE 3: SAVE ===
    new_leads = []
    log("\n--- Saving Results ---")
    
    for res in candidates:
        emails = res.get('emails', [])
        analysis = res.get('analysis', {})
        details = res.get('details', {})
        url = res['url']
        
        for email in emails:
             lead_id = add_lead(
                url, 
                email, 
                source=keywords, 
                category=", ".join(profile_names),
                industry=target_niche or details.get('industry', 'Detected'),
                business_type=details.get('business_type'),
                confidence=analysis.get('score'),
                relevance_reason=analysis.get('reason'),
                contact_person=details.get('contact_person'),
                company_name=details.get('business_name'),
                address=details.get('address'),
                phone_number=details.get('phone_number'),
                qualification_score=analysis.get('score'),
                qualification_reason=analysis.get('reason')
            )
             if lead_id:
                new_leads.append(res)
                log(f"✅ Saved: {url} ({email})")
                
                if auto_enrich:
                    log(f"  [Workflow] Auto-Enriching {url}...")
                    em = EnrichmentManager()
                    # We can do this sync here as we are already in an async function 
                    # but we are in a loop. To keep it simple, we await it.
                    await em.enrich_lead(lead_id)

    # CSV Export (Optional backup)
    if new_leads:
        timestamp = int(time.time())
        filename = f"leads_agentic_{timestamp}.csv"
        # ... (CSV logic if needed, keeping it minimal) ...
        
    log("Workflow completed.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    import argparse
    parser = argparse.ArgumentParser(description="B2B Outreach Tool")
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--profile", default="default", help="Pofiles")
    parser.add_argument("--niche", help="Target niche")
    
    args = parser.parse_args()
    
    query = " ".join(args.query) if args.query else config["search"]["keywords"][0]
    
    asyncio.run(run_outreach(query, profile_names=args.profile, target_niche=args.niche))
