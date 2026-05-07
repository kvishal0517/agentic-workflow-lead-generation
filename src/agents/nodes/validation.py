import dns.resolver
from email_validator import validate_email, EmailNotValidError
from src.agents.state import AgentState, LeadSchema
from src.utils.llm import llm
from loguru import logger

def check_mx(domain: str) -> bool:
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return len(records) > 0
    except Exception:
        return False

async def validation_node(state: AgentState) -> AgentState:
    logger.info("Starting Validation Node")
    validated_leads = []
    
    for lead in state['enriched_leads']:
        is_valid = True
        reason = "Passed all checks"
        
        # 1. Email validation (if exists)
        if lead.email:
            try:
                validate_email(lead.email, check_deliverability=False)
                if not check_mx(lead.domain):
                    is_valid = False
                    reason = "No MX records found for domain"
            except EmailNotValidError:
                is_valid = False
                reason = "Invalid email format"
        else:
            is_valid = False
            reason = "No email found"

        # 2. ICP Exclude check
        excludes = state['icp_config']['icp'].get('exclude', [])
        for ex in excludes:
            if ex.lower() in (lead.description or "").lower() or ex.lower() in (lead.company_name or "").lower():
                is_valid = False
                reason = f"Matches exclusion criteria: {ex}"
                break
        
        # 3. LLM Authenticity check
        if is_valid:
            auth_prompt = f"""
            Is the following business a genuine B2B service provider? 
            Check for red flags (freelancer, government, fortune 500, dead site).
            
            Company: {lead.company_name}
            Description: {lead.description}
            Website: {lead.website_url}
            
            Return JSON with "genuine" (bool) and "reason" (string).
            """
            try:
                import json
                res = await llm.call(auth_prompt, system_prompt="You are a fraud detection expert.", json_mode=True)
                data = json.loads(res)
                if not data.get("genuine", False):
                    is_valid = False
                    reason = data.get("reason", "LLM authenticity check failed")
            except Exception as e:
                logger.error(f"Validation LLM call failed for {lead.domain}: {e}")

        lead.is_valid = is_valid
        lead.validation_reason = reason
        if is_valid:
            validated_leads.append(lead)
            
    state['validated_leads'] = validated_leads
    logger.info(f"Validation Node: {len(validated_leads)} leads validated")
    return state
