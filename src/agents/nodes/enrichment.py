import re
from src.agents.state import AgentState, LeadSchema
from src.utils.search import scrape_page
from src.utils.llm import llm
from loguru import logger

EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

async def enrichment_node(state: AgentState) -> AgentState:
    logger.info("Starting Enrichment Node")
    enriched_leads = []
    
    for lead in state['raw_leads']:
        logger.info(f"Enriching {lead.domain}")
        content = await scrape_page(lead.website_url)
        
        # Simple email extraction
        emails = re.findall(EMAIL_REGEX, content)
        if emails:
            lead.email = emails[0] # Take first one
            
        # LLM enrichment for decision maker and business details
        enrich_prompt = f"""
        Analyze the following text from the website of {lead.domain} and extract:
        1. Name and Role of a decision maker (Founder/CEO/Owner).
        2. A brief 2-sentence description of what the business does.
        
        Website Content:
        {content[:1500]}
        
        Return JSON with keys: "decision_maker_name", "decision_maker_role", "description".
        """
        
        try:
            res = await llm.call(enrich_prompt, system_prompt="You are a business analyst. Output ONLY valid JSON.", json_mode=True)
            import json
            data = json.loads(res)
            lead.decision_maker_name = data.get("decision_maker_name")
            lead.decision_maker_role = data.get("decision_maker_role")
            lead.description = data.get("description", lead.description)
            lead.evidence.append({"type": "scraping", "content": content[:500]})
        except Exception as e:
            logger.error(f"Enrichment LLM call failed for {lead.domain}: {e}")
            
        enriched_leads.append(lead)
        
    state['enriched_leads'] = enriched_leads
    return state
