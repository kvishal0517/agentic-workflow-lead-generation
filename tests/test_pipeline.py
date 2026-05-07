import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.state import AgentState, LeadSchema
from src.agents.nodes.discovery import discovery_node
from src.agents.nodes.enrichment import enrichment_node

@pytest.mark.asyncio
async def test_discovery_node():
    state: AgentState = {
        "run_id": 1,
        "icp_config": {"icp": {"industries": ["Tech"], "roles": ["CEO"], "geography": ["USA"]}},
        "queries": [],
        "raw_leads": [],
        "enriched_leads": [],
        "validated_leads": [],
        "scored_leads": [],
        "final_leads": [],
        "error": None,
        "dry_run": True
    }
    
    with patch("src.utils.llm.llm.call", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"queries": ["tech companies USA"]}'
        
        with patch("src.utils.search.search_client.search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [{"title": "Test Co", "link": "https://test.com", "snippet": "Test snippet"}]
            
            new_state = await discovery_node(state)
            
            assert len(new_state["queries"]) > 0
            assert len(new_state["raw_leads"]) == 1
            assert new_state["raw_leads"][0].domain == "test.com"

@pytest.mark.asyncio
async def test_enrichment_node():
    state: AgentState = {
        "raw_leads": [LeadSchema(domain="test.com", website_url="https://test.com")],
        "enriched_leads": []
    }
    
    with patch("src.utils.search.scrape_page", new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = "Contact us at info@test.com. CEO is John Doe."
        
        with patch("src.utils.llm.llm.call", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = '{"decision_maker_name": "John Doe", "decision_maker_role": "CEO", "description": "Test business"}'
            
            new_state = await enrichment_node(state)
            
            assert new_state["enriched_leads"][0].email == "info@test.com"
            assert new_state["enriched_leads"][0].decision_maker_name == "John Doe"
