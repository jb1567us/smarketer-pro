import asyncio
import json
import argparse
import sys
import os
import csv
import subprocess
from datetime import datetime

# Add src to path to use existing LLM factory
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from config import config
from llm.factory import LLMFactory
import sys

# Force UTF-8 for Windows consoles to support emojis 🚀
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

class Orchestrator:
    def __init__(self):
        self.llm = LLMFactory.get_provider()
        self.directives = self._load_directives()
        
    def _load_directives(self):
        directives = {}
        d_path = os.path.join(os.path.dirname(__file__), 'directives')
        for name in ['discovery', 'qualification', 'enrichment', 'handover']:
            with open(os.path.join(d_path, f"{name}.md"), 'r', encoding='utf-8') as f:
                directives[name] = f.read()
        return directives

    def run_command(self, script_name, *args):
        """Runs a script in the execution/ folder and returns JSON output."""
        script_path = os.path.join(os.path.dirname(__file__), 'execution', script_name)
        cmd = [sys.executable, script_path] + list(args)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error running {script_name}: {e.stderr}")
            return None
        except json.JSONDecodeError:
            print(f"Error parsing JSON from {script_name}")
            return None

    async def run_mission(self, query, criteria=None):
        print(f"🚀 Starting Mission: {query}")
        print("--------------------------------")
        
        # 1. DISCOVERY
        print("\n[Phase 1] Discovery (Broad Net Code)")
        search_results = self.run_command('search_targets.py', query, '--limit', '20')
        
        if not search_results:
            print("❌ No results found. Aborting.")
            return

        print(f"✅ Found {len(search_results)} raw targets.")
        
        # 2. QUALIFICATION LOOPS
        print("\n[Phase 2 & 3] Qualification & Enrichment")
        qualified_leads = []
        
        for i, target in enumerate(search_results):
            url = target['url']
            print(f"\nProcessing ({i+1}/{len(search_results)}): {url}")
            
            # A. Scrape
            scrape_data = self.run_command('scrape_site.py', url)
            if not scrape_data or scrape_data.get('error'):
                print(f"  ⚠️ Scraping failed/skipped.")
                continue
                
            content = scrape_data.get('content', '')
            
            # B. Qualify (LLM Reasoning)
            print("  🤔 Agent Thinking (Qualification)...")
            
            # Construct Prompt
            base_directive = self.directives['qualification']
            user_criteria = criteria or "General Business Relevance"
            
            prompt = (
                f"{base_directive}\n\n"
                f"--- CONTEXT ---\n"
                f"Candidate URL: {url}\n"
                f"User Criteria: {user_criteria}\n"
                f"Site Content Preview: {content[:3000]}\n\n"
                f"--- INSTRUCTIONS ---\n"
                f"Evaluate this candidate. "
                f"Return valid JSON ONLY: {{'qualified': bool, 'score': int, 'reason': str}}"
            )
            
            try:
                response_text = self.llm.generate_text(prompt)
                
                # Robust JSON Extraction
                cleaned = response_text.strip()
                # Remove markdown fences
                if "```" in cleaned:
                    cleaned = cleaned.split("```json")[-1].split("```")[0].strip()
                    if "```" in cleaned: # Handle generic ``` block
                         cleaned = cleaned.split("```")[-1].strip()
                
                # Attempt to find JSON object bounds if strict parse fails
                try:
                    decision = json.loads(cleaned)
                except json.JSONDecodeError:
                    start = cleaned.find('{')
                    end = cleaned.rfind('}')
                    if start != -1 and end != -1:
                        decision = json.loads(cleaned[start:end+1])
                    else:
                        raise ValueError("No JSON object found")

            except Exception as e:
                print(f"  ❌ Agent Brain Error: {e}")
                continue
                
            if not decision.get('qualified'):
                print(f"  ❌ Rejected: {decision.get('reason')} (Score: {decision.get('score')})")
                continue
                
            print(f"  ✅ Qualified! Score: {decision.get('score')}")
            
            # 3. ENRICHMENT (Hybrid Trigger)
            # Simple heuristic check based on Directive (User wanted Hybrid w/ size trigger)
            # Since we don't have company size from scrape easily, we'll check for "generic email" trigger
            found_emails = scrape_data.get('emails', [])
            has_generic = any(e.startswith(('info@', 'contact@', 'sales@')) for e in found_emails)
            
            enrichment_data = {}
            if has_generic:
                print("  🔍 Generic email found. Triggering Deep Dive (Mock)...")
                domain = url.split('//')[-1].split('/')[0]
                enrichment_data = self.run_command('enrich_lead.py', domain)
            
            # 4. HANDOVER
            lead = {
                "url": url,
                "company_name": target.get('title'),
                "score": decision.get('score'),
                "reason": decision.get('reason'),
                "emails_scraped": found_emails,
                "enrichment": enrichment_data,
                "timestamp": datetime.now().isoformat()
            }
            qualified_leads.append(lead)
            self._save_lead(lead)
            
        print("\n✅ Mission Complete.")
        print(f"Generated {len(qualified_leads)} qualified leads.")

    def _save_lead(self, lead):
        file_exists = os.path.isfile('leads.csv')
        keys = ["url", "company_name", "score", "reason", "emails_scraped", "enrichment", "timestamp"]
        
        with open('leads_new.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            if not file_exists:
                writer.writeheader()
            
            # Flatten slightly for CSV
            row = lead.copy()
            row['emails_scraped'] = ", ".join(lead['emails_scraped'])
            row['enrichment'] = json.dumps(lead['enrichment'])
            writer.writerow(row)
            print(f"  💾 Saved to leads_new.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="What to look for (e.g. 'HVAC usage')")
    parser.add_argument("--criteria", help="Specific qualification rules", default=None)
    
    args = parser.parse_args()
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    orch = Orchestrator()
    asyncio.run(orch.run_mission(args.query, args.criteria))
