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
        """Standard draft generation."""
        return self.generate_optimized_email(context, instructions)

    def generate_optimized_email(self, context, instructions=None):
        """
        Ralph-Style Autonomous Optimization: 
        Generates a draft, critiques it, and iterates until high quality.
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
        """Internal helper for initial drafting."""
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
            base_instructions = (
                "Draft a highly personalized cold email for this lead.\n"
                "Rules:\n"
                "1. Use a hook relevant to their specific business.\n"
                "2. IF 'intent_signals', 'company_bio', or 'social_intel' are provided, prioritize mentioning them in the first 2 sentences.\n"
                "3. Keep it under 150 words.\n"
                "4. End with a soft call to action.\n"
                "5. NO generic fluff.\n\n"
                "Return JSON: {'subject_line': str, 'body': str, 'personalization_explanation': str}"
            )
        
        full_instructions = base_instructions
        if instructions:
            full_instructions += f"\n\nADDITIONAL USER INSTRUCTIONS:\n{instructions}"
            
        return self.provider.generate_json(f"Context for Email:\n{context}\n\n{full_instructions}")

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
        res = self.provider.generate_json(f"Context for DSR:\n{context}\n\n{instructions}")
        self.save_work(res, artifact_type="dsr_copy", metadata={"context_snippet": str(context)[:100]})
        return res

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
        res = self.provider.generate_json(f"Context for Sequence:\n{context}\n\n{instructions}")
        self.save_work(res, artifact_type="email_sequence", metadata={"steps": steps})
        return res

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
            suggestion_type = "Rewrite the CTA to be lower friction (e.g. 'Worth a chat?' vs 'Book a call')."
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

    def generate_seo_article(self, niche, keywords, target_url, anchor_text=None, use_spintax=False):
        """
        Generates a long-form SEO article for Web 2.0 or Article Directories.
        Optional: can return content in Spintax format.
        """
        if not anchor_text:
            anchor_text = keywords[0] if isinstance(keywords, list) else keywords

        spintax_rule = ""
        if use_spintax:
            spintax_rule = (
                "5. USE NESTED SPINTAX. Every sentence must have at least 3 variations using the {choice1|choice2|choice3} format.\n"
                "6. Ensure the result is valid nested spintax that can be parsed by standard tools.\n"
            )
        else:
            spintax_rule = (
                "5. NO SPINTAX. Write full, natural paragraphs.\n"
            )

        instructions = (
            f"Write a high-quality, informative SEO article about '{niche}'.\n"
            f"Target Keywords: {keywords}\n"
            "Rules:\n"
            "1. Length: 500-800 words.\n"
            "2. Structure: H1 title, intro, several sub-headings, and a conclusion.\n"
            "3. Tone: Informative, authoritative, but readable (not robotic).\n"
            f"4. Link Insertion: Naturally include a link to '{target_url}' using the anchor text '{anchor_text}'.\n"
            f"{spintax_rule}"
            "7. Ensure the content provides ACTUAL VALUE to a reader, not just keyword stuffing.\n\n"
            "Return JSON: {'title': str, 'body_markdown': str, 'summary': str, 'tags': list}"
        )
        res = self.provider.generate_json(f"SEO Article Request:\nNiche: {niche}\nKeywords: {keywords}\n\n{instructions}")
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
