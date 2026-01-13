import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from agents.wordpress import WordPressAgent
from dsr_manager import DSRManager
from database import get_platform_credentials

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dsr_test_harness")

async def run_dsr_test():
    # 1. Initialize Agents
    wp_agent = WordPressAgent()
    dsr_manager = DSRManager()
    
    # 2. Hardcoded cPanel Credentials (from session context)
    cpanel_url = "https://elk.lev3.com:2083"
    cp_user = "elliotspencermor"
    cp_pass = "!Meimeialibe4r"
    domain = "elk.lev3.com"
    directory = "dsr-test"

    logger.info(f"Step 1: Installing WordPress in /{directory}...")
    install_res = await wp_agent.cpanel_install_wp(
        cpanel_url, cp_user, cp_pass, domain, directory
    )
    
    if "error" in install_res:
        logger.error(f"Installation failed: {install_res['error']}")
        return

    logger.info(f"Step 2: WordPress installed at {install_res['url']}")
    site_url = install_res['url']
    admin_user = install_res['admin_user']
    admin_pass = install_res['admin_pass']

    logger.info("Step 3: Generating Application Password for REST API...")
    admin_dashboard_url = site_url.rstrip('/') + "/wp-admin"
    auth_res = await wp_agent.automate_app_password(admin_dashboard_url, admin_user, admin_pass)
    
    if "error" in auth_res:
        logger.error(f"App Password generation failed: {auth_res['error']}")
        return

    app_password = auth_res['app_password']
    logger.info(f"Step 4: API Access secured for user {admin_user}")

    # 3. Deploy a Test DSR
    logger.info("Step 5: Generating and Deploying Test DSR...")
    test_lead = {
        "id": 9999,
        "company_name": "Antigravity Testing Ltd",
        "industry": "Agentic AI & Automation",
        "category": "Tech",
        "pain_point": "manual workflow bottleneck",
        "headline": "Streamline Your Agency with Agentic OS",
        "sub_headline": "The future of B2B outreach is here.",
        "hero_text": "Stop spending hours on manual prospect research. Our autonomous agents handle the heavy lifting while you focus on closing.",
        "benefits": ["24/7 Autonomous Prospecting", "High-Conversion Copywriting", "Automated DSR Deployment"],
        "social_proof": "Antigravity helped us increase our lead volume by 300% in 2 weeks.",
        "cta": "Start Your Free Trial",
        "title": "Welcome Antigravity"
    }

    # Generate DSR (Draft)
    dsr_data = await dsr_manager.generate_dsr_for_lead(campaign_id=1, lead_data=test_lead)
    
    # Deploy DSR
    site_data = {
        "url": site_url,
        "username": admin_user,
        "app_password": app_password
    }
    
    deploy_res = await dsr_manager.deploy_dsr(dsr_data['id'], wp_agent, site_id=None, site_data=site_data)
    
    if "error" in deploy_res:
        logger.error(f"DSR Deployment failed: {deploy_res['error']}")
    else:
        logger.info(f"✅ SUCCESS! DSR Deployed to: {deploy_res['url']}")

if __name__ == "__main__":
    asyncio.run(run_dsr_test())
