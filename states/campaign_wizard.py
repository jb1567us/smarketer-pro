"""
Campaign Wizard State

Multi-step campaign creation with validation and preview
"""
import reflex as rx
from typing import Optional, Dict, Any, List


class CampaignWizardState(rx.State):
    """State for campaign wizard"""
    
    # Current step (0-3)
    current_step: int = 0
    
    # Step 1: Campaign Basics
    campaign_name: str = ""
    campaign_niche: str = ""
    product_name: str = ""
    product_context: str = ""
    selected_template: str = "custom"
    
    # Step 2: Lead Criteria
    target_company_size: str = "any"
    target_industries: List[str] = []
    target_locations: List[str] = []
    min_employees: int = 0
    max_employees: int = 10000
    
    # Step 3: Message Strategy
    message_tone: str = "professional"
    key_points: str = ""
    call_to_action: str = ""
    personalization_level: str = "high"
    
    # Validation
    step_errors: Dict[int, str] = {}
    is_valid: bool = False
    
    # Preview
    preview_message: str = ""
    
    # Templates
    templates: Dict[str, Dict[str, Any]] = {
        "saas": {
            "name": "SaaS Product",
            "tone": "professional",
            "key_points": "- Solve specific pain point\n- Show ROI\n- Offer free trial",
            "cta": "Book a demo"
        },
        "agency": {
            "name": "Agency Services",
            "tone": "casual",
            "key_points": "- Showcase portfolio\n- Highlight expertise\n- Social proof",
            "cta": "Schedule a call"
        },
        "startup": {
            "name": "Startup/Founder",
            "tone": "casual",
            "key_points": "- Personal story\n- Vision alignment\n- Mutual benefit",
            "cta": "Let's connect"
        },
        "custom": {
            "name": "Custom",
            "tone": "professional",
            "key_points": "",
            "cta": "Learn more"
        }
    }
    
    def apply_template(self, template_key: str):
        """Apply a campaign template"""
        self.selected_template = template_key
        template = self.templates.get(template_key, self.templates["custom"])
        
        self.message_tone = template["tone"]
        self.key_points = template["key_points"]
        self.call_to_action = template["cta"]
    
    def next_step(self):
        """Move to next step if current step is valid"""
        if self.validate_current_step():
            self.current_step = min(self.current_step + 1, 3)
    
    def previous_step(self):
        """Move to previous step"""
        self.current_step = max(self.current_step - 1, 0)
    
    def go_to_step(self, step: int):
        """Jump to specific step"""
        self.current_step = step
    
    def validate_current_step(self) -> bool:
        """Validate current step"""
        errors = {}
        
        if self.current_step == 0:
            # Step 1: Basics
            if not self.campaign_name.strip():
                errors[0] = "Campaign name is required"
            elif len(self.campaign_name) < 3:
                errors[0] = "Campaign name must be at least 3 characters"
            
            if not self.campaign_niche.strip():
                errors[0] = "Niche/industry is required"
            
            if not self.product_name.strip():
                errors[0] = "Product name is required"
        
        elif self.current_step == 1:
            # Step 2: Criteria (all optional with defaults)
            pass
        
        elif self.current_step == 2:
            # Step 3: Strategy
            if not self.key_points.strip():
                errors[2] = "Please add at least one key point"
            
            if not self.call_to_action.strip():
                errors[2] = "Call-to-action is required"
        
        self.step_errors = errors
        return len(errors) == 0
    
    def generate_preview(self):
        """Generate preview of campaign message"""
        # Simple preview generation
        preview = f"""Hi [First Name],

I noticed [Company Name] is in {self.campaign_niche}. I wanted to reach out about {self.product_name}.

{self.product_context}

Key benefits for you:
{self.key_points}

{self.call_to_action}

Best regards,
[Your Name]
"""
        self.preview_message = preview
    
    def create_campaign(self):
        """Create the campaign"""
        from backend.database import Database
        
        db = Database()
        campaign_data = {
            "name": self.campaign_name,
            "niche": self.campaign_niche,
            "product_name": self.product_name,
            "product_context": self.product_context,
            "status": "draft",
            "settings": {
                "template": self.selected_template,
                "tone": self.message_tone,
                "key_points": self.key_points,
                "cta": self.call_to_action,
                "criteria": {
                    "company_size": self.target_company_size,
                    "industries": self.target_industries,
                    "locations": self.target_locations,
                    "min_employees": self.min_employees,
                    "max_employees": self.max_employees
                }
            }
        }
        
        campaign_id = db.create_campaign(campaign_data)
        
        # Reset wizard
        self.reset_wizard()
        
        return campaign_id
    
    def reset_wizard(self):
        """Reset wizard to initial state"""
        self.current_step = 0
        self.campaign_name = ""
        self.campaign_niche = ""
        self.product_name = ""
        self.product_context = ""
        self.selected_template = "custom"
        self.target_company_size = "any"
        self.target_industries = []
        self.target_locations = []
        self.message_tone = "professional"
        self.key_points = ""
        self.call_to_action = ""
        self.step_errors = {}
        self.preview_message = ""
    
    @rx.var
    def progress_percentage(self) -> int:
        """Calculate progress percentage"""
        return int((self.current_step / 3) * 100)
    
    @rx.var
    def can_proceed(self) -> bool:
        """Check if can proceed to next step"""
        return self.validate_current_step()
    
    @rx.var
    def step_title(self) -> str:
        """Get current step title"""
        titles = [
            "Campaign Basics",
            "Lead Criteria",
            "Message Strategy",
            "Review & Launch"
        ]
        return titles[self.current_step]
