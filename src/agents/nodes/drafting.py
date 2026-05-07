from src.agents.state import AgentState, LeadSchema
from src.utils.llm import llm
from loguru import logger

async def drafting_node(state: AgentState) -> AgentState:
    logger.info("Starting Drafting Node")
    final_leads = []
    
    agency = state['icp_config']['agency']
    
    for lead in state['scored_leads']:
        draft_prompt = f"""
        Draft a personalized B2B outreach email for the following lead.
        
        Lead: {lead.company_name}
        Decision Maker: {lead.decision_maker_name} ({lead.decision_maker_role})
        Business Description: {lead.description}
        
        Our Agency: {agency['name']} - {agency['description']}
        
        Requirements:
        1. Subject line should be catchy.
        2. Body must include: Hook, Pain Point, Proof Point, Soft CTA.
        3. Total length under 140 words.
        4. Output format: HTML.
        
        Return JSON with "subject" and "body_html".
        """
        
        try:
            import json
            res = await llm.call(draft_prompt, system_prompt="You are a world-class sales copywriter.", json_mode=True)
            data = json.loads(res)
            lead.subject = data.get("subject")
            lead.body_html = data.get("body_html")
        except Exception as e:
            logger.error(f"Drafting LLM call failed for {lead.domain}: {e}")
            
        final_leads.append(lead)
        
    state['final_leads'] = final_leads
    return state
