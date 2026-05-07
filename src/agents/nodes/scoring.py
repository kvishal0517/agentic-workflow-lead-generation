from src.agents.state import AgentState, LeadSchema
from src.utils.llm import llm
from loguru import logger

async def scoring_node(state: AgentState) -> AgentState:
    logger.info("Starting Scoring Node")
    scored_leads = []
    
    icp = state['icp_config']['icp']
    
    for lead in state['validated_leads']:
        score = 50 # Base score
        breakdown = {"base": 50}
        
        # Rule-based scoring
        if lead.email:
            score += 10
            breakdown["has_email"] = 10
        if lead.decision_maker_name:
            score += 10
            breakdown["has_decision_maker"] = 10
            
        # LLM qualitative scoring
        score_prompt = f"""
        Rate this lead on a scale of 0-50 based on how well it matches the ICP.
        
        ICP: {icp}
        
        Lead Company: {lead.company_name}
        Lead Description: {lead.description}
        Lead Industry: {lead.industry}
        
        Return JSON with "qualitative_score" (int) and "justification" (string).
        """
        
        try:
            import json
            res = await llm.call(score_prompt, system_prompt="You are a sales operations manager.", json_mode=True)
            data = json.loads(res)
            qual_score = data.get("qualitative_score", 0)
            score += qual_score
            breakdown["llm_match"] = qual_score
            breakdown["justification"] = data.get("justification", "")
        except Exception as e:
            logger.error(f"Scoring LLM call failed for {lead.domain}: {e}")

        lead.score = float(score)
        lead.score_breakdown = breakdown
        scored_leads.append(lead)
        
    # Sort and pick top 10
    scored_leads.sort(key=lambda x: x.score, reverse=True)
    state['scored_leads'] = scored_leads[:10]
    logger.info(f"Scoring Node: Ranked {len(scored_leads)} leads, kept top 10")
    return state
