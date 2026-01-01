
import sys
import os
sys.path.append(os.path.abspath("src"))
from database import init_db, add_lead
import time

print("Initializing DB...")
init_db()

# Mock mock candidate data structure from workflow.py
candidates = [
    {
        "url": "http://repro-test.com",
        "emails": ["contact@repro-test.com"],
        "analysis": {"score": 90, "reason": "Perfect match"},
        "details": {
            "business_name": "Repro Corp",
            "address": "404 Error St",
            "phone_number": "555-4321",
            "industry": "Debugging",
            "business_type": "Software",
            "contact_person": "Bug Hunter"
        }
    }
]

keywords = "test query"
profile_names = ["debug_profile"]
target_niche = "IT"

print("Starting simulated save loop...")
new_leads = []
for res in candidates:
    emails = res.get('emails', [])
    analysis = res.get('analysis', {})
    details = res.get('details', {})
    url = res['url']
    
    for email in emails:
        print(f"Attempting to save: {email}")
        try:
            result = add_lead(
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
            print(f"add_lead returned: {result}")
            if result:
                 new_leads.append(res)
                 print(f"✅ Saved: {url} ({email})")
            else:
                 print(f"❌ Failed (Likely duplicate): {email}")
        except Exception as e:
            print(f"💥 Exception during save: {e}")

print("Save loop complete.")
