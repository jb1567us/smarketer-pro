from .base import BaseAgent
import json
from prompt_engine import PromptEngine, PromptContext

class CopywriterAgent(BaseAgent):
    def __init__(self, provider=None, role="B2B Email Copywriter", goal="Draft highly personalized, persuasive, and human-sounding cold emails based on verified lead data."):
        super().__init__(
            role=role,
            goal=goal,
            provider=provider
        )
        self.prompt_engine = PromptEngine()

    async def think_async(self, context, instructions=None):
        """Async entry point. Handles generic content tasks or delegates to email logic."""
        # Check for generic content generation triggers (e.g. for WordPress site building)
        prompt_lower = str(context).lower()
        if "json list" in prompt_lower or "website pages" in prompt_lower or "article" in prompt_lower:
            # Direct generation for site content
            self.logger.info(f"  [Copywriter] Handling generic content request via think_async")
            return self.provider.generate_json(context)
        
        # Check for Creative/Specialized Writing Triggers
        if "social media" in prompt_lower or "tiktok" in prompt_lower or "instagram" in prompt_lower:
            # Simple heuristic detection - in a real app, use an intent classifier
            return self.generate_social_strategy(context, "Product/Service", "Social Media") # Default args if not parsed
        
        if "ad copy" in prompt_lower or "advertisement" in prompt_lower:
            return self.generate_ad_copy("Product/Service", "General", "Conversion")

        if "persona" in prompt_lower or "icp" in prompt_lower:
            return self.generate_persona(context)
            
        if "brainstorm" in prompt_lower or "ideas" in prompt_lower:
            return self.brainstorm_angles(context, "General Ideation")
        
        # Default to existing email logic (blocking call is acceptable for now)
        return self.think(context, instructions)

    def think(self, context, instructions=None):
        """Standard draft generation with routing."""
        # Check for Creative/Specialized Writing Triggers (Sync Version)
        prompt_lower = (str(context) + " " + str(instructions)).lower()
        
        if "social media" in prompt_lower or "tiktok" in prompt_lower or "instagram" in prompt_lower:
            return self.generate_social_strategy(context, "Product/Service", "Social Media")
        
        if "ad copy" in prompt_lower or "advertisement" in prompt_lower:
            return self.generate_ad_copy("Product/Service", "General", "Conversion")

        if "persona" in prompt_lower or "icp" in prompt_lower:
            return self.generate_persona(context)
            
        if "brainstorm" in prompt_lower or "ideas" in prompt_lower:
            return self.brainstorm_angles(context, "General Ideation")
            
        return self.generate_optimized_email(context, instructions)

    def generate_optimized_email(self, context, instructions=None):
        """
        Context should include:
        - Lead info (Business type, pain points, contact name)
        - Value Proposition (what we are selling)
        - Enrichment Data (Intent signals, social profiles, social_intel)
        """
        from config import config
        personalization_level = config.get('campaign', {}).get('personalization', 'hyper')
        
        # 1. Initial Draft
        self.logger.info("  [Copywriter] Generating initial draft...")
        draft = self._draft_email(context, instructions, personalization_level)
        
        # 2. Ralph Loop: Critique and Iterate
        max_iterations = 2
        for i in range(max_iterations):
            self.logger.info(f"  [Copywriter] Ralph Critique Loop {i+1}/{max_iterations}...")
            
            critique_prompt = (
                f"You are a critical Sales Manager. Critique this cold email draft:\n\n"
                f"SUBJECT: {draft.get('subject_line')}\n"
                f"BODY: {draft.get('body')}\n\n"
                "Check for:\n"
                "1. Fluff/Generic intros (e.g. 'I hope this finds you well')\n"
                "2. Length (too long?)\n"
                "3. Personalization (does it actually use the context provided?)\n"
                "4. CTA (is it soft and effective?)\n\n"
                "Return JSON: {'score': int (1-10), 'issues': list, 'suggestions': str}"
            )
            
            critique = self.provider.generate_json(critique_prompt)
            score = critique.get('score', 0)
            
            if score >= 8:
                self.logger.info(f"  ✅ Draft passed with score {score}/10.")
                break
            
            self.logger.info(f"  ⚠️ Draft score {score}/10. Refining based on suggestions...")
            
            # 3. Refine
            refine_prompt = (
                f"Refine the following cold email based on this critique: {critique.get('suggestions')}\n\n"
                f"Original Subject: {draft.get('subject_line')}\n"
                f"Original Body: {draft.get('body')}\n\n"
                f"Context: {context}\n\n"
                "Return JSON: {'subject_line': str, 'body': str, 'personalization_explanation': str}"
            )
            draft = self.provider.generate_json(refine_prompt)
            
        self.save_work(json.dumps(draft), artifact_type="text", metadata={"context": "optimized_email_draft", "iterations": i+1})
        return draft

    def _draft_email(self, context, instructions, personalization_level):
        """Internal helper for initial drafting using Prompt Engine."""
        # 1. Use existing Hub context if available, else create a default Kernel
        if self.context:
            ctx = self.context
            self.report_to_hub("FETCH_CONTEXT", "Using Hub Brand Kernel for drafting.")
        else:
            ctx = PromptContext(
                niche="General Business", # Default if unknown
                icp_role="Decision Maker",
                brand_voice="Professional and Persuasive"
            )
            self.report_to_hub("DEFAULT_CONTEXT", "No Hub context found, using defaults.")
        
        # If context is a dict (advanced usage), parse it
        # (This allows us to upgrade the caller later without breaking this)
        if isinstance(context, dict):
            ctx.niche = context.get('niche', ctx.niche)
            ctx.icp_role = context.get('role', ctx.icp_role)
        
        # 2. Render Prompt
        prompt = self.prompt_engine.get_prompt(
            "copywriter/email_cold.j2", 
            ctx, 
            instruction_override=instructions,
            raw_context=str(context) # Pass the original raw context string for the LLM to see specific lead details
        )
            
        return self.provider.generate_json(f"Context for Email:\n{context}\n\n{prompt}")

    def write_grounded_outreach(self, icp, offering, candidate, extracted_signals, decision):
        """
        Hyper-specific outreach messages grounded in provided evidence.
        """
        prompt = self.prompt_engine.get_prompt(
            "copywriter/grounded_outreach_writer.j2",
            PromptContext(niche=icp.get('icp_name', 'B2B'), icp_role='Copywriter'), # Minimal kernel, vars passed in kwargs
            icp=icp,
            offering=offering,
            candidate=candidate,
            extracted=extracted_signals,
            decision=decision
        )
        if prompt.startswith("ERROR"):
            self.logger.error(f"Render Error: {prompt}")
            return {"messages": [], "error": prompt}
        return self.generate_json(prompt)

    async def write_grounded_outreach_async(self, icp, offering, candidate, extracted_signals, decision):
        """
        Async version of write_grounded_outreach.
        """
        prompt = self.prompt_engine.get_prompt(
            "copywriter/grounded_outreach_writer.j2",
            PromptContext(niche=icp.get('icp_name', 'B2B'), icp_role='Copywriter'),
            icp=icp,
            offering=offering,
            candidate=candidate,
            extracted=extracted_signals,
            decision=decision
        )
        if prompt.startswith("ERROR"):
            self.logger.error(f"Render Error: {prompt}")
            return {"messages": [], "error": prompt}
        return await self.generate_json_async(prompt)

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
        res = self.provider.generate_json(prompt)
        self.save_work(res, artifact_type="campaign_optimization", metadata={"problem": problem})
        return res

    def generate_seo_article(self, niche, keywords, target_url=None, anchor_text=None, use_spintax=False, affiliate_links=None):
        """
        Generates a long-form SEO article using Prompt Engine.
        """
        # 1. Build Kernel
        ctx = PromptContext(
            niche=niche,
            icp_role="Reader searching for solution",
            icp_pain_points=["Lack of information", "Need for expert advice"],
            brand_voice="Authoritative and Helpful"
        )
        
        # 2. Render Prompt
        prompt = self.prompt_engine.get_prompt(
            "copywriter/seo_article.j2",
            ctx,
            keywords=keywords,
            target_url=target_url,
            anchor_text=anchor_text,
            use_spintax=use_spintax,
            affiliate_links=affiliate_links
        )
        
        res = self.provider.generate_json(f"Context: {niche}\n\n{prompt}")
        self.save_work(res, artifact_type="seo_article", metadata={"niche": niche, "target_url": target_url})
        return res

    def generate_spintax(self, content):
        """
        Converts an existing piece of content into nested Spintax format.
        """
        prompt = f"""
        Convert the following content into HIGHLY VARIED nested spintax.
        
        RULES:
        1. Every sentence must have at least 3-5 variations using {{choice1|choice2|choice3}} format.
        2. Use synonyms and alternative phrasing.
        3. Do NOT change the meaning or remove any links/placeholders.
        4. The goal is >80% uniqueness between generated versions.
        
        Content:
        {content}
        
        Return the full content in Spintax format.
        """
        res = self.provider.generate_text(prompt)
        self.save_work(res, artifact_type="spintax_content", metadata={"content_preview": content[:50]})
        return res
    def generate_social_strategy(self, niche, product_name, platform="General"):
        """
        Generates a social media strategy using Prompt Engine.
        Absorbed from SocialMediaAgent.
        """
        ctx = PromptContext(niche=niche, icp_role="Target Audience")
        prompt = self.prompt_engine.get_prompt(
            "copywriter/social_strategy.j2",
            ctx,
            platform=platform,
            product_name=product_name
        )
        res = self.provider.generate_json(prompt)
        self.save_work(res, artifact_type="social_strategy", metadata={"platform": platform})
        return res

    def generate_ad_copy(self, product_name, platform, goal, niche="General", persona=None):
        """
        Generates ad copy.
        Absorbed from AdCopyAgent.
        """
        ctx = PromptContext(niche=niche, icp_role=persona)
        prompt = self.prompt_engine.get_prompt(
            "copywriter/ad_copy.j2",
            ctx,
            product_name=product_name,
            platform=platform,
            goal=goal
        )
        res = self.provider.generate_json(prompt)
        self.save_work(res, artifact_type="ad_copy", metadata={"platform": platform})
        return res

    def brainstorm_angles(self, topic, goal, niche="General"):
        """
        Brainstorms creative angles.
        Absorbed from BrainstormerAgent.
        """
        ctx = PromptContext(niche=niche, icp_role="Target Audience")
        prompt = self.prompt_engine.get_prompt(
            "copywriter/brainstorm.j2",
            ctx,
            topic=topic,
            goal=goal
        )
        res = self.provider.generate_json(prompt)
        self.save_work(res, artifact_type="brainstorm", metadata={"topic": topic})
        return res

    def generate_persona(self, niche, role="Decision Maker"):
        """
        Generates an ICP/Persona.
        Absorbed from PersonaAgent.
        """
        ctx = PromptContext(niche=niche, icp_role=role)
        prompt = self.prompt_engine.get_prompt(
            "copywriter/persona_icp.j2",
            ctx
        )
        res = self.provider.generate_json(prompt)
        self.save_work(res, artifact_type="persona", metadata={"niche": niche})
        return res
