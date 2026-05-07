import json
from urllib.parse import urlparse
from src.agents.state import AgentState, LeadSchema
from src.utils.llm import llm
from src.utils.search import search_client
from loguru import logger

async def discovery_node(state: AgentState) -> AgentState:
    logger.info("Starting Discovery Node")
    icp = state['icp_config']
    
    # 1. Generate Queries
    query_prompt = f"""
    Based on the following ICP (Ideal Customer Profile), generate 5 specific Google search queries to find potential B2B leads.
    Target Industries: {icp['icp']['industries']}
    Target Roles: {icp['icp']['roles']}
    Geography: {icp['icp']['geographies']}
    
    Return the queries as a JSON list of strings.
    """
    
    try:
        query_response = await llm.call(query_prompt, system_prompt="You are a search expert. Output ONLY valid JSON.", json_mode=True)
        queries = json.loads(query_response)
        if isinstance(queries, dict): queries = queries.get("queries", [])
    except Exception as e:
        logger.error(f"Failed to generate queries: {e}")
        queries = [f"{ind} companies in {state['icp_config']['icp']['geographies'][0]}" for ind in state['icp_config']['icp']['industries']]

    state['queries'] = queries
    
    # 2. Run Searches
    raw_leads_dict = {}
    for query in queries:
        results = await search_client.search(query)
        for res in results:
            domain = urlparse(res['link']).netloc
            if domain and domain not in raw_leads_dict:
                raw_leads_dict[domain] = LeadSchema(
                    domain=domain,
                    website_url=res['link'],
                    company_name=res['title'],
                    description=res['snippet'],
                    evidence=[{"type": "search_result", "url": res['link'], "content": res['snippet']}]
                )
    
    state['raw_leads'] = list(raw_leads_dict.values())
    logger.info(f"Discovery Node found {len(state['raw_leads'])} raw leads")
    return state
