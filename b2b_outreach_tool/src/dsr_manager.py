import json
import asyncio
from agents import CopywriterAgent, GraphicsDesignerAgent
from database import create_dsr, update_dsr_wp_info, get_dsr_by_lead

class DSRManager:
    def __init__(self):
        self.copywriter = CopywriterAgent()
        self.designer = GraphicsDesignerAgent()

    async def generate_dsr_for_lead(self, campaign_id, lead_data):
        """
        Orchestrates full DSR content generation.
        lead_data: dict with lead details
        """
        # Check if already exists
        existing = get_dsr_by_lead(campaign_id, lead_data['id'])
        if existing:
            return existing

        lead_context = json.dumps(lead_data, indent=2)
        
        # 1. Generate Copy
        copy_res = self.copywriter.generate_dsr_copy(f"Lead:\n{lead_context}")
        
        # 2. Generate Hero Image
        # Design a prompt based on the lead's industry and pain points
        industry = lead_data.get('industry') or lead_data.get('category') or 'business'
        pain = lead_data.get('pain_point') or 'efficiency'
        image_prompt = f"Professional hero image for a {industry} business landing page, focusing on solving {pain}, modern and sleek design."
        
        image_res = self.designer.think(image_prompt)
        
        # 3. Assemble full content
        content = {
            "copy": copy_res,
            "hero_image": image_res.get('local_path') or image_res.get('image_url')
        }
        
        # 4. Save to DB (draft state)
        dsr_id = create_dsr(
            campaign_id=campaign_id,
            lead_id=lead_data['id'],
            title=copy_res.get('title', f"Welcome {lead_data.get('company_name', 'Visitor')}"),
            content_json=json.dumps(content)
        )
        
        return {
            "id": dsr_id,
            "campaign_id": campaign_id,
            "lead_id": lead_data['id'],
            "content": content,
            "status": "draft"
        }

    async def deploy_dsr(self, dsr_id, wp_agent, site_id, site_data):
        """
        Deploys an existing DSR to WordPress.
        """
        from database import get_connection
        import sqlite3
        
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM digital_sales_rooms WHERE id = ?', (dsr_id,))
        dsr = c.fetchone()
        conn.close()
        
        if not dsr:
            return {"error": "DSR not found"}
        
        content = json.loads(dsr['content_json'])
        copy = content['copy']
        image_url = content['hero_image']
        
        # Create HTML payload
        html_payload = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="background: url('{image_url}') center/cover no-repeat; height: 300px; border-radius: 10px 10px 0 0; display: flex; align-items: center; justify-content: center; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                <h1 style="font-size: 2.5em; text-align: center; padding: 0 20px;">{copy['headline']}</h1>
            </div>
            <div style="padding: 30px;">
                <h2 style="color: #333;">{copy['sub_headline']}</h2>
                <p style="font-size: 1.1em; color: #555; line-height: 1.6;">{copy['hero_text']}</p>
                
                <h3 style="margin-top: 30px; border-bottom: 2px solid #5d5fef; padding-bottom: 10px;">Why Partner With Us?</h3>
                <ul style="list-style: none; padding-left: 0;">
                    {''.join([f'<li style="padding: 10px 0; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center;"><span style="color: #5d5fef; margin-right: 15px; font-weight: bold;">✓</span> {benefit}</li>' for benefit in copy['benefits']])}
                </ul>
                
                <div style="background: #fdfdfd; padding: 20px; border-left: 5px solid #5d5fef; margin: 30px 0; font-style: italic;">
                    "{copy['social_proof']}"
                </div>
                
                <div style="text-align: center; margin-top: 40px;">
                    <a href="#" style="background: #5d5fef; color: white; padding: 15px 40px; text-decoration: none; font-weight: bold; border-radius: 50px; font-size: 1.2em; display: inline-block;">{copy['cta']}</a>
                </div>
            </div>
        </div>
        """
        
        # Deploy to WP
        # Manage content takes: wp_url, wp_user, wp_pass, action, data={}
        wp_res = await wp_agent.manage_content(
            site_data['url'],
            site_data['username'],
            site_data['app_password'],
            "create_page",
            {"title": copy['title'], "content": html_payload, "status": "publish"}
        )
        
        if "id" in wp_res:
            update_dsr_wp_info(dsr_id, wp_res['id'], wp_res['link'])
            return {"success": True, "url": wp_res['link']}
        else:
            return {"error": wp_res.get('error', 'Deployment failed')}
