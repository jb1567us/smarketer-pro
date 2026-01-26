import sys
import os
import asyncio
import csv
import time
import aiohttp
import functools
import json

# Appends src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
    
    if not keywords:
        log("❌ Error: No keywords provided. Aborting workflow.")
        return
    
    init_db()
    
    # Initialize Proxies
    from proxy_manager import proxy_manager
    await proxy_manager.fetch_proxies()
    
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
        candidates = []
        
        # [Phase 3] Adaptive Throttling
        # Concurrency limit from config (Default: 20)
        config_limit = config.get("search", {}).get("concurrency", 20)
        
        # Check System RAM
        import psutil
        try:
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024 ** 3)
            # Safe heuristic: 4 threads per GB of FREE RAM
            # Each chrome instance + python overhead ~ 250MB worst case
            resilient_limit = max(1, int(available_gb * 4))
            
            limit = min(config_limit, resilient_limit)
            log(f"  [System] Adaptive Throttling: RAM Free={available_gb:.1f}GB. Adjusted Concurrency: {limit} (Config: {config_limit})")
        except:
             limit = config_limit
        
        sem = asyncio.Semaphore(limit)

        # Debug Stats
        source_counts = {"organic": 0, "listing": 0}
        for u in urls:
            st = u.get("source_type", "organic") if isinstance(u, dict) else "organic"
            source_counts[st] = source_counts.get(st, 0) + 1
        log(f"  [Debug] Candidates Source Breakdown: {source_counts}")

        async def process_candidate(candidate):
            async with sem:
                # Dead Letter Queue Context
                dlq_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "failed_leads.jsonl")
                
                try:
                    # Handle legacy string format just in case, but prefer dict
                    if isinstance(candidate, str):
                        url = candidate
                        source_type = "organic"
                    else:
                        url = candidate.get("url")
                        source_type = candidate.get("source_type", "organic")

                    log(f"  > Processing {url} ({source_type})...")
                    
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
                            details = {}
                            has_emails = bool(intel.get('emails'))
                            
                            if has_emails:
                                 log(f"    ⚡ Emails found ({len(intel.get('emails'))}). FAST SAVE.")
                                 details = {
                                     "company_name": "Unknown (Fast Save)", 
                                     "confidence": 0.9
                                 }
                            else:
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
                
                except Exception as e:
                    # [Phase 3] Dead Letter Queue
                    log(f"    🔥 CRITICAL FAILURE for {candidate}: {e}. Saved to DLQ.")
                    try:
                        with open(dlq_path, "a", encoding="utf-8") as f:
                            f.write(json.dumps({"candidate": candidate, "error": str(e), "time": time.time()}) + "\n")
                    except:
                        pass # Double fail shouldn't crash loop
                    return None

        tasks = [process_candidate(u) for u in urls]
        # Use return_exceptions=True to ensure gather doesn't crash on unhandled exceptions
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results and log errors
        candidates = []
        for r in results:
            if isinstance(r, Exception):
                log(f"    ⚠️ Task failed: {r}")
                # Also Log to DLQ if not already handled
            elif r:
                candidates.append(r)
        
        # --- RALPH-STYLE CAPTCHA HEALING ---
        healed_raw = await researcher.process_captcha_queue()
        if healed_raw:
            log(f"\n--- Phase 2.5: Captcha Healing ({len(healed_raw)} leads) ---")
            for res in healed_raw:
                try:
                    log(f"  [Agent] Evaluating HEALED candidate: {res['url']}")
                    # Simplified qualification for healed leads to avoid full recursion
                    q_context = f"Company URL: {res['url']}\nContent: {res.get('html_preview', '')[:3000]}\nCriteria: {icp_criteria}"
                    qualification = qualifier.think(q_context)
                    if qualification.get('qualified'):
                        log(f"    ✅ Healed lead qualified!")
                        candidates.append({
                            "url": res['url'],
                            "emails": res.get('emails', []),
                            "analysis": qualification,
                            "intel": res,
                            "details": {} # Optional: could run analyze_content here too
                        })
                    else:
                        log(f"    ❌ Healed lead rejected: {qualification.get('reason')}")
                except Exception as e:
                    log(f"    ⚠️ Error qualifying healed lead: {e}")

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
        
        # === POST-PROCESS ENGINE ===
        try:
            log("\n--- Triggering Automation Engine ---")
            from engine.core import WorkflowEngine
            from engine.loader import WorkflowLoader
            import nodes # Register Core Nodes

            
            # Load Test Workflow (In production this would be dynamic)
            # using absolute path relative to this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            workflow_path = os.path.join(base_dir, "workflows", "test_workflow.json")
            
            if os.path.exists(workflow_path):
                engine = WorkflowEngine()
                workflow_def = WorkflowLoader.load_from_file(workflow_path)
                
                # Pass context (the new leads)
                payload = {"new_leads_count": len(new_leads), "leads": new_leads}
                
                execution_id = await engine.run_workflow(workflow_def, payload)
                log(f"✅ Automation Engine Triggered! Execution ID: {execution_id}")
            else:
                log(f"⚠️ Workflow file not found at {workflow_path}")
                
        except Exception as e:
            log(f"❌ Automation Engine Error: {e}")

    log("Workflow completed.")
    return new_leads

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
