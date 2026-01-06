from .base import BaseAgent
import json

class CopywriterAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="B2B Email Copywriter",
            goal="Draft highly personalized, persuasive, and human-sounding cold emails based on verified lead data.",
            provider=provider
        )

    def think(self, context, instructions=None):
        """
        Context should include:
        - Lead info (Business type, pain points, contact name)
        - Value Proposition (what we are selling)
        - Enrichment Data (Intent signals, social profiles, social_intel)
        """
        from config import config
        personalization_level = config.get('campaign', {}).get('personalization', 'hyper')
        
        base_instructions = ""
        if personalization_level == 'generic':
             base_instructions = (
                "Draft a professional cold email for this lead.\n"
                "Rules:\n"
                "1. Use a clear, standard value proposition.\n"
                "2. Keep it under 100 words.\n"
                "3. Focus on general industry benefits rather than specific company details.\n"
                "4. Return JSON: {'subject_line': str, 'body': str, 'personalization_explanation': 'Generic mode active'}"
             )
        else:
            # Hyper personalization (default)
            base_instructions = (
                "Draft a highly personalized cold email for this lead.\n"
                "Rules:\n"
                "1. Use a hook relevant to their specific business.\n"
                "2. IF 'intent_signals', 'company_bio', or 'social_intel' are provided, prioritize mentioning them in the first 2 sentences to show deep research.\n"
                "3. Keep it under 150 words.\n"
                "4. End with a soft call to action (e.g. 'Worth a chat?').\n"
                "5. Do NOT use generic fluff like 'I hope this finds you well'.\n\n"
                "Return JSON: {'subject_line': str, 'body': str, 'personalization_explanation': str}"
            )
        
        full_instructions = base_instructions
        if instructions:
            full_instructions += f"\n\nADDITIONAL USER INSTRUCTIONS:\n{instructions}"
            
        result = self.provider.generate_json(f"Context for Email:\n{context}\n\n{full_instructions}")
        self.save_work(json.dumps(result), artifact_type="text", metadata={"context": "email_draft"})
        return result

    def generate_dsr_copy(self, context):
        """
        Generates copy for a Digital Sales Room landing page.
        Context should include lead info and value prop.
        """
        instructions = (
            "Create a hyper-personalized Digital Sales Room (landing page) for this lead.\n"
            "Output must include:\n"
            "1. Headline: A powerful, benefit-driven title tailored to their business.\n"
            "2. Sub-headline: A persuasive follow-up explaining the unique value.\n"
            "3. Personal Hero Section: 2-3 sentences welcoming them and addressing their specific pain point.\n"
            "4. Three Key Benefits: Bullet points mapped to their business needs.\n"
            "5. Social Proof Sentence: A trust-building statement.\n"
            "6. Call to Action: A clear next step.\n\n"
            "Return JSON: {'title': str, 'headline': str, 'sub_headline': str, 'hero_text': str, 'benefits': list, 'social_proof': str, 'cta': str}"
        )
        return self.provider.generate_json(f"Context for DSR:\n{context}\n\n{instructions}")

    def generate_sequence(self, context, steps=3):
        """
        Generates a multi-step outreach sequence.
        Returns a list of steps with touch_type, delay, subject, and body.
        """
        instructions = (
            f"Draft a {steps}-step outreach sequence for this lead.\n"
            "Each step should have a different angle:\n"
            "Step 1: The 'Hook' (Intro + relevant benefit using intent_signals/social_intel if available)\n"
            "Step 2: The 'Value' (Specific case study or feature explanation relevant to company_bio)\n"
            "Step 3: The 'Nudge' or 'Break-up' (Final soft touch explaining why this matters now)\n\n"
            "Rules:\n"
            "1. Vary the tone but keep it consistent with the brand.\n"
            "2. Keep each email under 120 words.\n"
            "3. Return a JSON list of steps.\n\n"
            "Return JSON: [\n"
            "  {'step_number': 1, 'touch_type': 'email', 'delay_days': 0, 'subject': str, 'body': str},\n"
            "  {'step_number': 2, 'touch_type': 'email', 'delay_days': 3, 'subject': str, 'body': str},\n"
            "  ...\n"
            "]"
        )
        return self.provider.generate_json(f"Context for Sequence:\n{context}\n\n{instructions}")

    def optimize_campaign(self, current_copy, performance_stats):
        """
        Self-corrects based on analytics data.
        """
        open_rate = performance_stats.get('open_rate', 0)
        click_rate = performance_stats.get('click_rate', 0)
        
        problem = ""
        suggestion_type = ""
        
        if open_rate < 0.25:
            problem = f"Low Open Rate ({open_rate*100:.1f}%). The subject line is likely too generic or spammy."
            suggestion_type = "Generate 3 alternative subject lines that are more curiosity-inducing or personal."
        elif click_rate < 0.05:
            problem = f"Low Click Rate ({click_rate*100:.1f}%). The CTA is weak or the value prop isn't clear."
            suggestion_type = "Rewrite the CTA to be lower friction (e.g. 'Worth a look?' vs 'Book a call')."
        else:
            return {"status": "good", "message": "Campaign performing well."}
            
        prompt = f"""
        Analyze this campaign performance failure:
        Current Subject: "{current_copy.get('subject')}"
        Current Body: "{current_copy.get('body')}"
        
        Problem: {problem}
        Task: {suggestion_type}
        
        Return JSON: {{ "diagnosis": "...", "optimized_variants": ["variant1", "variant2"] }}
        """
        return self.provider.generate_json(prompt)
